import {cfg,dbHeaders,disabled,isEnabled,json,serverError,verifyMember} from './_common.mjs';
export async function onRequestPost({request,env}){
  if(!isEnabled(env))return disabled();
  try{
    const userId=await verifyMember(request,env);
    if(!userId)return json({status:'forbidden'},403);
    const {base,key}=cfg(env);
    const u=new URL(`${base}/rest/v1/card_qr_qa_tokens`);
    u.searchParams.set('user_id',`eq.${userId}`);
    const r=await fetch(u,{method:'PATCH',redirect:'error',headers:dbHeaders(key,{
      'content-type':'application/json','prefer':'return=minimal'
    }),body:JSON.stringify({revoked_at:new Date().toISOString()})});
    return r.ok?json({status:'revoked'}):serverError();
  }catch{return serverError();}
}
