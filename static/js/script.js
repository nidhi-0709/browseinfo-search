const form=document.querySelector("form");

if(form){

form.addEventListener("submit",()=>{

const btn=document.querySelector("button");

btn.innerHTML="Searching...";

btn.disabled=true;

});

}