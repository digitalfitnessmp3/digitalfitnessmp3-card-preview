import {cfg,dbHeaders,disabled,digestToken,isEnabled,json,newToken,serverError,verifyMember} from './_common.mjs';
// QA-only issuance. Default deny and exactly one preverified BASIC non-admin account.
export async function onRequestPost({request,env}){
  if(!isEnabled(env))return disabled();
  try{
    const userId=await verifyMember(request,env);
    if(!userId)return json({status:'forbidden'},403);
    const token=newToken(), hash=await digestToken(token);
    const {base,key}=cfg(env);
    const expires=new Date(Date.now()+30*24*3600*1000).toISOString();
    const u=new URL(`${base}/rest/v1/card_qr_qa_tokens`);
    u.searchParams.set('on_conflict','user_id');
    const r=await fetch(u,{method:'POST',redirect:'error',headers:dbHeaders(key,{
      'content-type':'application/json','prefer':'resolution=merge-duplicates,return=minimal'
    }),body:JSON.stringify({user_id:userId,token_digest:hash,revoked_at:null,expires_at:expires})});
    if(!r.ok)return serverError();
    const verificationUrl=new URL('/card-verifica.html',env.CARD_PUBLIC_ORIGIN);
    // Fragment identifiers do not appear in initial HTTP requests or proxy URL logs.
    verificationUrl.hash='code='+token;
    return json({status:'issued',verification_url:verificationUrl.toString(),expires_at:expires});
  }catch{return serverError();}
}
