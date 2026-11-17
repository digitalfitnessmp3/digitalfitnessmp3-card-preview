// AlphaBeat World Card — isolated QA helpers. No user data in responses.
export const json = (data, status=200) => new Response(JSON.stringify(data), {status, headers:{
  'content-type':'application/json; charset=utf-8',
  'cache-control':'no-store, private',
  'referrer-policy':'no-referrer',
  'x-content-type-options':'nosniff'
}});
export const disabled = () => json({status:'not_enabled'},503);
export const isEnabled = env => env.CARD_QA_ENABLED === 'true' && !!env.SUPABASE_URL && !!env.SUPABASE_SERVICE_ROLE_KEY && !!env.CARD_PUBLIC_ORIGIN && !!env.CARD_QA_USER_ID && env.CARD_QA_ACCOUNT_CLASS === 'basic_non_admin_verified';
export function cfg(env){
  const url = new URL(env.SUPABASE_URL);
  if(url.protocol!=='https:' || url.username || url.password || url.search || url.hash) throw Error('invalid_supabase_url');
  return {base:url.origin, key:env.SUPABASE_SERVICE_ROLE_KEY};
}
export const base64url = arr => Array.from(arr,b=>String.fromCharCode(b)).join('');
export async function digestToken(token){
  const d=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(token));
  return Array.from(new Uint8Array(d)).map(x=>x.toString(16).padStart(2,'0')).join('');
}
export function newToken(){const b=crypto.getRandomValues(new Uint8Array(32));
  // Browser/WebCrypto compatible base64url without Node APIs.
  return btoa(base64url(b)).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'');
}
export function validToken(v){return typeof v==='string' && /^[A-Za-z0-9_-]{43}$/.test(v);}
export function dbHeaders(key,more={}){return {'apikey':key,'authorization':`Bearer ${key}`,...more};}
export async function verifyMember(request,env){
  if(env.CARD_QA_ACCOUNT_CLASS!=='basic_non_admin_verified' || !/^[0-9a-f-]{36}$/i.test(env.CARD_QA_USER_ID||''))return null;
  const bearer=request.headers.get('authorization')||'';
  if(!/^Bearer [A-Za-z0-9._-]{20,4096}$/.test(bearer))return null;
  let origin;
  try {origin=new URL(env.CARD_PUBLIC_ORIGIN).origin;
    if(new URL(env.CARD_PUBLIC_ORIGIN).protocol!=='https:' || origin!==new URL(request.url).origin)return null;
  }catch{return null;}
  if(request.headers.get('origin') && request.headers.get('origin')!==origin)return null;
  const {base,key}=cfg(env);
  const r=await fetch(`${base}/auth/v1/user`,{headers:{'apikey':key,'authorization':bearer},redirect:'error'});
  if(!r.ok)return null;
  const user=await r.json();
  if(user.id!==env.CARD_QA_USER_ID || !user.email_confirmed_at)return null;
  const m=user.app_metadata||{};
  const roles=[m.role,m.user_role,m.account_role,m.access_level].map(x=>String(x||'').toLowerCase());
  if(roles.some(x=>/(^|[^a-z])(admin|owner|staff|superuser|qa)([^a-z]|$)/.test(x)))return null;
  const adminIds=(env.CARD_ADMIN_USER_IDS||'').split(',').map(x=>x.trim());
  if(adminIds.includes(user.id))return null;
  return user.id;
}
export function serverError(){return json({status:'service_unavailable'},503);}
