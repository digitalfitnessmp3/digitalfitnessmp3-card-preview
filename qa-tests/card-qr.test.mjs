import assert from 'node:assert/strict';
import {test} from 'node:test';
import {onRequestPost as verify} from '../functions/api/card/verify.js';
import {onRequestPost as issue} from '../functions/api/card/issue.js';
import {onRequestPost as revoke} from '../functions/api/card/revoke.js';
import {newToken,digestToken,validToken} from '../functions/api/card/_common.mjs';

const id='aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee';
const env = {
  CARD_QA_ENABLED:'true', CARD_QA_USER_ID:id, CARD_QA_ACCOUNT_CLASS:'basic_non_admin_verified',
  CARD_PUBLIC_ORIGIN:'https://qa.example.test',CARD_ADMIN_USER_IDS:'bbbbbbbb-bbbb-4ccc-8ddd-eeeeeeeeeeee',
  SUPABASE_URL:'https://supabase.example.test',SUPABASE_SERVICE_ROLE_KEY:'test-service-secret'
};
const req=(path='/api/card/verify',method='GET',headers={},data)=>new Request('https://qa.example.test'+path,{method,headers,body:data});
const verifyReq=code=>req('/api/card/verify','POST',{'content-type':'application/json'},JSON.stringify({code}));
const body=async r=>({status:r.status,content:await r.json(),headers:r.headers});
const bearer={authorization:'Bearer '+('z'.repeat(45)),origin:'https://qa.example.test'};
const oldFetch=globalThis.fetch;
async function withFetch(mock,fn){globalThis.fetch=mock;try{return await fn()}finally{globalThis.fetch=oldFetch}}
const reply=(data,status=200)=>new Response(JSON.stringify(data),{status,headers:{'content-type':'application/json'}});

test('default deny: no secrets, no pilot, no backend calls',async()=>{
  await withFetch(()=>{throw Error('called');},async()=>{
    for(const action of [verify,issue,revoke]){
      const r=await action({request:req('/api/card/verify','POST'),env:{}});
      assert.equal(r.status,503);
      assert.equal((await r.json()).status,'not_enabled');
    }
  });
});
test('token is 256-bit random, encoded and hashed',async()=>{
  const a=newToken(),b=newToken();
  assert.equal(a.length,43);assert.ok(validToken(a));assert.notEqual(a,b);
  assert.match(await digestToken(a),/^[0-9a-f]{64}$/);
  assert.ok(!validToken('not-a-token'));
});
test('missing or malformed code gives invalid without DB call',async()=>{
  await withFetch(()=>{throw Error('called');},async()=>{
    const r=await verify({request:verifyReq('wrong'),env});
    assert.deepEqual((await body(r)).content,{status:'invalid'});
  });
});
test('QR status responses are minimal: valid, revoked, expired, unknown',async()=>{
  const code=newToken();
  for(const [rows,want] of [
    [[{revoked_at:null,expires_at:'2099-01-01T00:00:00Z'}],'valid'],
    [[{revoked_at:'2026-11-17T01:00:00Z',expires_at:'2099-01-01T00:00:00Z'}],'revoked'],
    [[{revoked_at:null,expires_at:'2020-01-01T00:00:00Z'}],'expired'],
    [[], 'invalid']
  ]){
    await withFetch(async(_url,opts)=>{assert.equal(opts.method,undefined);return reply(rows);},async()=>{
      const r=await verify({request:verifyReq(code),env});
      const b=await body(r);
      assert.equal(b.content.status,want);
      assert.equal(b.headers.get('cache-control'),'no-store, private');
      assert.ok(!JSON.stringify(b.content).includes(id));
      assert.ok(!JSON.stringify(b.content).includes(code));
      assert.ok(!JSON.stringify(b.content).includes('email'));
    });
  }
});
test('verification backend failure is fail closed',async()=>{
  await withFetch(()=>reply({},502),async()=>{
    const r=await verify({request:verifyReq(newToken()),env});
    assert.deepEqual((await body(r)).content,{status:'service_unavailable'});
  });
});
test('issue is denied when missing bearer and never writes',async()=>{
  await withFetch(()=>{throw Error('called');},async()=>{
    const r=await issue({request:req('/api/card/issue','POST'),env});
    assert.equal(r.status,403);
  });
});
test('pilot issue rejects owner/admin, unknown and unconfirmed accounts',async()=>{
  for(const user of [
    {id,app_metadata:{role:'admin'},email_confirmed_at:'2020-01-01'},
    {id:'cccccccc-bbbb-4ccc-8ddd-eeeeeeeeeeee',app_metadata:{},email_confirmed_at:'2020-01-01'},
    {id,app_metadata:{},email_confirmed_at:null}
  ]){
    await withFetch(async(url)=>{
      if(String(url).includes('/auth/v1/user'))return reply(user);
      throw Error('unexpected write');
    },async()=>{
      const r=await issue({request:req('/api/card/issue','POST',bearer),env});
      assert.equal(r.status,403);
    });
  }
});
test('pilot issue creates only digest, response gets scan URL',async()=>{
  const calls=[];
  await withFetch(async(url,opts)=>{
    calls.push({url:String(url),opts});
    if(String(url).includes('/auth/v1/user'))return reply({id,app_metadata:{role:'member'},email_confirmed_at:'2026-11-01'});
    return new Response(null,{status:201});
  },async()=>{
    const r=await issue({request:req('/api/card/issue','POST',bearer),env});
    const b=await body(r);assert.equal(b.status,200);
    assert.equal(b.content.status,'issued');
    const url=new URL(b.content.verification_url);assert.equal(url.origin,env.CARD_PUBLIC_ORIGIN);
    assert.equal(url.search,''); const token=new URLSearchParams(url.hash.slice(1)).get('code');assert.ok(validToken(token));
    const stored=JSON.parse(calls[1].opts.body);
    assert.equal(stored.user_id,id);
    assert.equal(stored.token_digest,await digestToken(token));
    assert.ok(!calls[1].opts.body.includes(token));
    assert.ok(!JSON.stringify(b.content).includes(id));
  });
});
test('revoke can only target the confirmed member',async()=>{
  let target;
  await withFetch(async(url,opts)=>{
    if(String(url).includes('/auth/v1/user'))return reply({id,app_metadata:{role:'member'},email_confirmed_at:'2026-11-01'});
    target=String(url);
    assert.equal(opts.method,'PATCH');
    return new Response(null,{status:204});
  },async()=>{
    const r=await revoke({request:req('/api/card/revoke','POST',bearer),env});
    assert.equal((await body(r)).content.status,'revoked');
    assert.ok(target.includes('eq.'+id));
  });
});
test('cross-origin issuance denied',async()=>{
  await withFetch(()=>{throw Error('called');},async()=>{
    const r=await issue({request:req('/api/card/issue','POST',{...bearer,origin:'https://malicious.example.test'}),env});
    assert.equal(r.status,403);
  });
});
