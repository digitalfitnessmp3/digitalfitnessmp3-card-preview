import {cfg,dbHeaders,disabled,isEnabled,json,serverError,verifyMember} from './_common.mjs';
// Read-only: the logged-in pilot can check card status, but never retrieve its secret.
export async function onRequestGet({request,env}){
  if(!isEnabled(env))return disabled();
  try{
    const userId=await verifyMember(request,env);
    if(!userId)return json({status:'forbidden'},403);
    const {base,key}=cfg(env);
    const url=new URL(base+'/rest/v1/card_qr_qa_tokens');
    url.searchParams.set('user_id','eq.'+userId);
    url.searchParams.set('select','expires_at,revoked_at');
    url.searchParams.set('limit','1');
    const r=await fetch(url,{headers:dbHeaders(key),redirect:'error'});
    if(!r.ok)return serverError();
    const rows=await r.json();
    if(!Array.isArray(rows))return serverError();
    if(!rows.length)return json({status:'not_issued'});
    const card=rows[0];
    if(card.revoked_at)return json({status:'revoked'});
    if(!card.expires_at||Date.parse(card.expires_at)<=Date.now())return json({status:'expired'});
    return json({status:'active',tier:'BASIC',expires_at:card.expires_at});
  }catch{return serverError();}
}
