import assert from 'node:assert/strict';
import {test} from 'node:test';
import {onRequestGet as me} from '../functions/api/card/me.js';
const userId='aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee';
const env={CARD_QA_ENABLED:'true',CARD_QA_USER_ID:userId,CARD_QA_ACCOUNT_CLASS:'basic_non_admin_verified',
CARD_PUBLIC_ORIGIN:'https://qa.example.test',CARD_ADMIN_USER_IDS:'bbbbbbbb-bbbb-4ccc-8ddd-eeeeeeeeeeee',
SUPABASE_URL:'https://supabase.example.test',SUPABASE_SERVICE_ROLE_KEY:'test-service-secret'};
const req=(headers={})=>new Request('https://qa.example.test/api/card/me',{headers});
const bearer={authorization:'Bearer '+('z'.repeat(45)),origin:'https://qa.example.test'};
async function mockFetch(handler,fn){const old=globalThis.fetch;globalThis.fetch=handler;try{await fn()}finally{globalThis.fetch=old;}}
const reply=(value,status=200)=>new Response(JSON.stringify(value),{status,headers:{'content-type':'application/json'}});
test('status endpoint defaults disabled',async()=>{
  await mockFetch(()=>{throw Error('unexpected fetch')},async()=>{
    const r=await me({request:req(),env:{}});assert.equal(r.status,503);assert.equal((await r.json()).status,'not_enabled');
  });
});
test('no bearer cannot read any card',async()=>{
  await mockFetch(()=>{throw Error('unexpected fetch')},async()=>{
    const r=await me({request:req(),env});assert.equal(r.status,403);
  });
});
test('missing admin list fails closed',async()=>{
  await mockFetch(()=>{throw Error('unexpected fetch')},async()=>{
    const r=await me({request:req(bearer),env:{...env,CARD_ADMIN_USER_IDS:''}});assert.equal(r.status,503);
  });
});
test('member state is minimal and never exposes UID, email, or QR token',async()=>{
  for(const [rows,want] of [
    [[], 'not_issued'],
    [[{expires_at:'2099-01-01T00:00:00Z',revoked_at:null}],'active'],
    [[{expires_at:'2099-01-01T00:00:00Z',revoked_at:'2026-11-01T00:00:00Z'}],'revoked'],
    [[{expires_at:'2020-01-01T00:00:00Z',revoked_at:null}],'expired']]){
    let calls=0;
    await mockFetch(async(url)=>{
      calls++;
      if(String(url).includes('/auth/v1/user'))return reply({id:userId,email_confirmed_at:'2026-11-01T00:00:00Z',app_metadata:{role:'member'}});
      assert.ok(String(url).includes('user_id=eq.'));
      return reply(rows);
    },async()=>{
      const r=await me({request:req(bearer),env});
      assert.equal(r.status,200);
      const out=await r.json();
      assert.equal(out.status,want);assert.equal(calls,2);
      assert.ok(!JSON.stringify(out).includes(userId));
      assert.ok(!('email' in out));assert.ok(!('verification_url' in out));assert.ok(!('token_digest' in out));
      assert.equal(r.headers.get('cache-control'),'no-store, private');
    });
  }
});
test('database errors fail closed',async()=>{
  await mockFetch(async url=>String(url).includes('/auth/v1/user')?
    reply({id:userId,email_confirmed_at:'2026-11-01T00:00:00Z',app_metadata:{role:'member'}}):reply({},503),
    async()=>{const r=await me({request:req(bearer),env});assert.equal(r.status,503);}
  );
});
test('admin metadata is denied',async()=>{
  for(const app_metadata of [{role:'admin'},{is_admin:true},{is_owner:true}]){
    await mockFetch(async url=>{
      assert.ok(String(url).includes('/auth/v1/user'));
      return reply({id:userId,email_confirmed_at:'2026-11-01T00:00:00Z',app_metadata});
    },async()=>{
      const r=await me({request:req(bearer),env});
      assert.equal(r.status,403);
    });
  }
});
