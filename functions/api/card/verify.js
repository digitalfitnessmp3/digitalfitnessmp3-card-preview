import {cfg,dbHeaders,disabled,digestToken,isEnabled,json,serverError,validToken} from './_common.mjs';
// Public verification is read-only. Scanning never authenticates a visitor.
export async function onRequestPost({request,env}){
  if(!isEnabled(env))return disabled();
  // Parse only a small JSON body; never put a bearer-like code in server URL logs.
  if(request.headers.get('content-type')?.split(';')[0].trim()!=='application/json')return json({status:'invalid'});
  const length=Number(request.headers.get('content-length')||0);
  if(length>256)return json({status:'invalid'});
  let code;
  try {const raw=await request.text(); if(raw.length>256)return json({status:'invalid'});code=JSON.parse(raw).code;}
  catch{return json({status:'invalid'});}
  if(!validToken(code))return json({status:'invalid'});
  try{
    const {base,key}=cfg(env);
    const hash=await digestToken(code);
    const u=new URL(`${base}/rest/v1/card_qr_qa_tokens`);
    u.searchParams.set('token_digest',`eq.${hash}`);
    u.searchParams.set('select','revoked_at,expires_at');
    u.searchParams.set('limit','1');
    const r=await fetch(u,{headers:dbHeaders(key),redirect:'error'});
    if(!r.ok)return serverError();
    const rows=await r.json();
    if(!Array.isArray(rows)||rows.length===0)return json({status:'invalid'});
    const row=rows[0];
    if(row.revoked_at)return json({status:'revoked'});
    if(!row.expires_at || Date.parse(row.expires_at)<=Date.now())return json({status:'expired'});
    return json({status:'valid',tier:'BASIC'});
  }catch{return serverError();}
}
