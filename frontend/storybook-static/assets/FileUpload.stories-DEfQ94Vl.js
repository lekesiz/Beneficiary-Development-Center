import{j as e,c as B}from"./utils-BAIen5-9.js";import{r as c}from"./index-CleY8y_P.js";import{c as g,B as F}from"./Button--t4ZV3r3.js";import{F as Ve}from"./file-text-BdmJ-Oca.js";import"./_commonjsHelpers-Cpj98o6Y.js";/**
 * @license lucide-react v0.294.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const _e=g("Archive",[["rect",{width:"20",height:"5",x:"2",y:"3",rx:"1",key:"1wp1u1"}],["path",{d:"M4 8v11a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8",key:"1s80jp"}],["path",{d:"M10 12h4",key:"a56b0p"}]]);/**
 * @license lucide-react v0.294.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const qe=g("Image",[["rect",{width:"18",height:"18",x:"3",y:"3",rx:"2",ry:"2",key:"1m3agn"}],["circle",{cx:"9",cy:"9",r:"2",key:"af1f0g"}],["path",{d:"m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21",key:"1xmnt7"}]]);/**
 * @license lucide-react v0.294.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Ie=g("Music",[["path",{d:"M9 18V5l12-2v13",key:"1jmyc2"}],["circle",{cx:"6",cy:"18",r:"3",key:"fqmcym"}],["circle",{cx:"18",cy:"16",r:"3",key:"1hluhg"}]]);/**
 * @license lucide-react v0.294.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const E=g("Upload",[["path",{d:"M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4",key:"ih7n3h"}],["polyline",{points:"17 8 12 3 7 8",key:"t8dd8p"}],["line",{x1:"12",x2:"12",y1:"3",y2:"15",key:"widbto"}]]);/**
 * @license lucide-react v0.294.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Ae=g("Video",[["path",{d:"m22 8-6 4 6 4V8Z",key:"50v9me"}],["rect",{width:"14",height:"12",x:"2",y:"6",rx:"2",ry:"2",key:"1rqjg6"}]]);/**
 * @license lucide-react v0.294.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Be=g("X",[["path",{d:"M18 6 6 18",key:"1bl5f8"}],["path",{d:"m6 6 12 12",key:"d8bk6v"}]]),Oe=s=>s.startsWith("image/")?e.jsx(qe,{className:"h-5 w-5"}):s.startsWith("video/")?e.jsx(Ae,{className:"h-5 w-5"}):s.startsWith("audio/")?e.jsx(Ie,{className:"h-5 w-5"}):s.includes("zip")||s.includes("rar")||s.includes("tar")?e.jsx(_e,{className:"h-5 w-5"}):e.jsx(Ve,{className:"h-5 w-5"}),O=s=>{if(s===0)return"0 Bytes";const t=1024,n=["Bytes","KB","MB","GB"],a=Math.floor(Math.log(s)/Math.log(t));return parseFloat((s/Math.pow(t,a)).toFixed(2))+" "+n[a]},h=({onUpload:s,onRemove:t,maxFiles:n=5,maxSize:a=10*1024*1024,acceptedTypes:i=["*/*"],multiple:x=!0,disabled:m=!1,className:we,uploadedFiles:u=[],showPreview:Se=!0})=>{const[ke,q]=c.useState(!1),[d,W]=c.useState(!1),[$,I]=c.useState([]),De=r=>a&&r.size>a?`File size exceeds ${O(a)}`:i.length>0&&!i.includes("*/*")&&!i.some(p=>p.endsWith("/*")?r.type.startsWith(p.slice(0,-1)):r.type===p)?`File type ${r.type} is not accepted`:null,f=c.useCallback(async r=>{const l=Array.from(r),p=[];u.length+l.length>n&&p.push(`Maximum ${n} files allowed`);const A=[];if(l.forEach(v=>{const j=De(v);j?p.push(`${v.name}: ${j}`):A.push(v)}),I(p),A.length>0){W(!0);try{await s(A)}catch{I(j=>[...j,"Upload failed. Please try again."])}finally{W(!1)}}},[u.length,n,s]),Ue=c.useCallback(r=>{if(r.preventDefault(),q(!1),m||d)return;const l=r.dataTransfer.files;l.length>0&&f(l)},[m,d,f]),Ce=c.useCallback(r=>{r.preventDefault(),!m&&!d&&q(!0)},[m,d]),ze=c.useCallback(r=>{r.preventDefault(),q(!1)},[]),Me=c.useCallback(r=>{const l=r.target.files;l&&l.length>0&&f(l),r.target.value=""},[f]),y=!m&&!d&&u.length<n;return e.jsxs("div",{className:B("w-full",we),children:[e.jsx("div",{className:B("border-2 border-dashed rounded-lg p-6 transition-colors",ke?"border-primary bg-primary/5":"border-gray-300 hover:border-gray-400",m&&"opacity-50 cursor-not-allowed",!y&&"bg-gray-50"),onDrop:Ue,onDragOver:Ce,onDragLeave:ze,children:e.jsxs("div",{className:"text-center",children:[e.jsx(E,{className:B("mx-auto h-12 w-12 mb-4",y?"text-gray-400":"text-gray-300")}),e.jsxs("div",{className:"mb-4",children:[e.jsx("p",{className:"text-sm text-gray-600 mb-1",children:y?"Drag and drop files here, or click to select":`Maximum ${n} files reached`}),i.length>0&&i[0]!=="*/*"&&e.jsxs("p",{className:"text-xs text-gray-500",children:["Accepted: ",i.join(", ")]}),e.jsxs("p",{className:"text-xs text-gray-500",children:["Max size: ",O(a)]})]}),y&&e.jsx("div",{children:e.jsxs(F,{variant:"outline",disabled:m||d,loading:d,className:"relative",children:[e.jsx(E,{className:"h-4 w-4 mr-2"}),d?"Uploading...":"Select Files",e.jsx("input",{type:"file",className:"absolute inset-0 w-full h-full opacity-0 cursor-pointer",multiple:x,accept:i.join(","),onChange:Me,disabled:m||d})]})})]})}),$.length>0&&e.jsxs("div",{className:"mt-4 p-3 bg-red-50 border border-red-200 rounded-md",children:[e.jsx("div",{className:"text-sm text-red-700",children:$.map((r,l)=>e.jsx("div",{children:r},l))}),e.jsx(F,{variant:"ghost",size:"sm",onClick:()=>I([]),className:"mt-2 text-red-600 hover:text-red-800",children:"Dismiss"})]}),Se&&u.length>0&&e.jsxs("div",{className:"mt-4",children:[e.jsxs("h4",{className:"text-sm font-medium text-gray-900 mb-2",children:["Uploaded Files (",u.length,")"]}),e.jsx("div",{className:"space-y-2",children:u.map(r=>e.jsxs("div",{className:"flex items-center justify-between p-3 bg-gray-50 rounded-md",children:[e.jsxs("div",{className:"flex items-center space-x-3",children:[e.jsx("div",{className:"text-gray-500",children:Oe(r.type)}),e.jsxs("div",{className:"flex-1 min-w-0",children:[e.jsx("p",{className:"text-sm font-medium text-gray-900 truncate",children:r.name}),e.jsx("p",{className:"text-xs text-gray-500",children:O(r.size)})]})]}),e.jsxs("div",{className:"flex items-center space-x-2",children:[r.progress!==void 0&&r.progress<100&&e.jsx("div",{className:"w-20 bg-gray-200 rounded-full h-2",children:e.jsx("div",{className:"bg-primary h-2 rounded-full transition-all",style:{width:`${r.progress}%`}})}),r.error&&e.jsx("span",{className:"text-xs text-red-600",children:r.error}),r.url&&e.jsx(F,{variant:"ghost",size:"sm",onClick:()=>window.open(r.url,"_blank"),className:"text-xs",children:"View"}),t&&e.jsx(F,{variant:"ghost",size:"sm",onClick:()=>t(r.id),className:"text-red-600 hover:text-red-800",children:e.jsx(Be,{className:"h-4 w-4"})})]})]},r.id))})]})]})};try{h.displayName="FileUpload",h.__docgenInfo={description:"",displayName:"FileUpload",props:{onUpload:{defaultValue:null,description:"",name:"onUpload",required:!0,type:{name:"(files: File[]) => Promise<UploadedFile[]>"}},onRemove:{defaultValue:null,description:"",name:"onRemove",required:!1,type:{name:"((fileId: string) => void) | undefined"}},maxFiles:{defaultValue:{value:"5"},description:"",name:"maxFiles",required:!1,type:{name:"number | undefined"}},maxSize:{defaultValue:{value:"10 * 1024 * 1024"},description:"",name:"maxSize",required:!1,type:{name:"number | undefined"}},acceptedTypes:{defaultValue:{value:"['*/*']"},description:"",name:"acceptedTypes",required:!1,type:{name:"string[] | undefined"}},multiple:{defaultValue:{value:"true"},description:"",name:"multiple",required:!1,type:{name:"boolean | undefined"}},disabled:{defaultValue:{value:"false"},description:"",name:"disabled",required:!1,type:{name:"boolean | undefined"}},className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string | undefined"}},uploadedFiles:{defaultValue:{value:"[]"},description:"",name:"uploadedFiles",required:!1,type:{name:"UploadedFile[] | undefined"}},showPreview:{defaultValue:{value:"true"},description:"",name:"showPreview",required:!1,type:{name:"boolean | undefined"}}}}}catch{}const Pe={title:"UI/FileUpload",component:h,parameters:{layout:"centered",docs:{description:{component:"A comprehensive file upload component with drag-and-drop, validation, and progress tracking."}}},tags:["autodocs"],argTypes:{multiple:{control:"boolean",description:"Allow multiple file uploads"},accept:{control:"text",description:'Accepted file types (e.g., "image/*", ".pdf,.doc")'},maxSize:{control:"number",description:"Maximum file size in bytes"},onChange:{control:!1,description:"Callback when files change"},onRemove:{control:!1,description:"Callback when a file is removed"},disabled:{control:"boolean",description:"Disable the upload component"},className:{control:"text",description:"Additional CSS classes"}}},o=s=>{const[t,n]=c.useState([]);return e.jsxs("div",{className:"w-[500px]",children:[e.jsx(h,{...s,value:t,onChange:n,onRemove:a=>{n(t.filter((i,x)=>x!==a))}}),t.length>0&&e.jsxs("div",{className:"mt-4 p-4 bg-gray-50 rounded",children:[e.jsx("h4",{className:"font-semibold mb-2",children:"Selected Files:"}),e.jsx("ul",{className:"space-y-1",children:t.map((a,i)=>e.jsxs("li",{className:"text-sm",children:[a.name," (",(a.size/1024).toFixed(2)," KB)"]},i))})]})]})},b={render:s=>e.jsx(o,{...s}),args:{}},N={render:s=>e.jsx(o,{...s}),args:{multiple:!1}},w={render:s=>e.jsx(o,{...s}),args:{multiple:!0}},S={render:s=>e.jsx(o,{...s}),args:{accept:"image/*",multiple:!0}},k={render:s=>e.jsx(o,{...s}),args:{accept:".pdf,.doc,.docx,.txt",multiple:!0}},D={render:s=>e.jsx(o,{...s}),args:{maxSize:1024*1024,multiple:!0}},U={render:s=>e.jsx(o,{...s}),args:{maxSize:50*1024*1024,multiple:!0}},C={render:s=>e.jsx(o,{...s}),args:{disabled:!0}},z={render:()=>{const s=[new File(["Content 1"],"document1.pdf",{type:"application/pdf"}),new File(["Content 2"],"image1.jpg",{type:"image/jpeg"})],[t,n]=c.useState(s);return e.jsx("div",{className:"w-[500px]",children:e.jsx(h,{value:t,onChange:n,onRemove:a=>{n(t.filter((i,x)=>x!==a))},multiple:!0})})}},M={render:s=>e.jsx(o,{...s}),args:{accept:"video/*",maxSize:100*1024*1024,multiple:!1}},V={render:s=>e.jsx(o,{...s}),args:{accept:".xlsx,.xls,.csv",multiple:!0}},_={render:s=>e.jsx(o,{...s}),args:{className:"border-blue-500 bg-blue-50",multiple:!0}};var L,R,P;b.parameters={...b.parameters,docs:{...(L=b.parameters)==null?void 0:L.docs,source:{originalSource:`{
  render: args => <FileUploadDemo {...args} />,
  args: {}
}`,...(P=(R=b.parameters)==null?void 0:R.docs)==null?void 0:P.source}}};var K,X,G;N.parameters={...N.parameters,docs:{...(K=N.parameters)==null?void 0:K.docs,source:{originalSource:`{
  render: args => <FileUploadDemo {...args} />,
  args: {
    multiple: false
  }
}`,...(G=(X=N.parameters)==null?void 0:X.docs)==null?void 0:G.source}}};var H,Z,J;w.parameters={...w.parameters,docs:{...(H=w.parameters)==null?void 0:H.docs,source:{originalSource:`{
  render: args => <FileUploadDemo {...args} />,
  args: {
    multiple: true
  }
}`,...(J=(Z=w.parameters)==null?void 0:Z.docs)==null?void 0:J.source}}};var Q,Y,T;S.parameters={...S.parameters,docs:{...(Q=S.parameters)==null?void 0:Q.docs,source:{originalSource:`{
  render: args => <FileUploadDemo {...args} />,
  args: {
    accept: 'image/*',
    multiple: true
  }
}`,...(T=(Y=S.parameters)==null?void 0:Y.docs)==null?void 0:T.source}}};var ee,se,re;k.parameters={...k.parameters,docs:{...(ee=k.parameters)==null?void 0:ee.docs,source:{originalSource:`{
  render: args => <FileUploadDemo {...args} />,
  args: {
    accept: '.pdf,.doc,.docx,.txt',
    multiple: true
  }
}`,...(re=(se=k.parameters)==null?void 0:se.docs)==null?void 0:re.source}}};var ae,te,ne;D.parameters={...D.parameters,docs:{...(ae=D.parameters)==null?void 0:ae.docs,source:{originalSource:`{
  render: args => <FileUploadDemo {...args} />,
  args: {
    maxSize: 1024 * 1024,
    // 1MB
    multiple: true
  }
}`,...(ne=(te=D.parameters)==null?void 0:te.docs)==null?void 0:ne.source}}};var le,ie,oe;U.parameters={...U.parameters,docs:{...(le=U.parameters)==null?void 0:le.docs,source:{originalSource:`{
  render: args => <FileUploadDemo {...args} />,
  args: {
    maxSize: 50 * 1024 * 1024,
    // 50MB
    multiple: true
  }
}`,...(oe=(ie=U.parameters)==null?void 0:ie.docs)==null?void 0:oe.source}}};var ce,de,me;C.parameters={...C.parameters,docs:{...(ce=C.parameters)==null?void 0:ce.docs,source:{originalSource:`{
  render: args => <FileUploadDemo {...args} />,
  args: {
    disabled: true
  }
}`,...(me=(de=C.parameters)==null?void 0:de.docs)==null?void 0:me.source}}};var pe,ue,ge;z.parameters={...z.parameters,docs:{...(pe=z.parameters)==null?void 0:pe.docs,source:{originalSource:`{
  render: () => {
    // Create mock files for demonstration
    const mockFiles = [new File(['Content 1'], 'document1.pdf', {
      type: 'application/pdf'
    }), new File(['Content 2'], 'image1.jpg', {
      type: 'image/jpeg'
    })];
    const [files, setFiles] = useState<File[]>(mockFiles);
    return <div className="w-[500px]">
        <FileUpload value={files} onChange={setFiles} onRemove={index => {
        setFiles(files.filter((_, i) => i !== index));
      }} multiple />
      </div>;
  }
}`,...(ge=(ue=z.parameters)==null?void 0:ue.docs)==null?void 0:ge.source}}};var xe,he,fe;M.parameters={...M.parameters,docs:{...(xe=M.parameters)==null?void 0:xe.docs,source:{originalSource:`{
  render: args => <FileUploadDemo {...args} />,
  args: {
    accept: 'video/*',
    maxSize: 100 * 1024 * 1024,
    // 100MB
    multiple: false
  }
}`,...(fe=(he=M.parameters)==null?void 0:he.docs)==null?void 0:fe.source}}};var ye,ve,je;V.parameters={...V.parameters,docs:{...(ye=V.parameters)==null?void 0:ye.docs,source:{originalSource:`{
  render: args => <FileUploadDemo {...args} />,
  args: {
    accept: '.xlsx,.xls,.csv',
    multiple: true
  }
}`,...(je=(ve=V.parameters)==null?void 0:ve.docs)==null?void 0:je.source}}};var Fe,be,Ne;_.parameters={..._.parameters,docs:{...(Fe=_.parameters)==null?void 0:Fe.docs,source:{originalSource:`{
  render: args => <FileUploadDemo {...args} />,
  args: {
    className: 'border-blue-500 bg-blue-50',
    multiple: true
  }
}`,...(Ne=(be=_.parameters)==null?void 0:be.docs)==null?void 0:Ne.source}}};const Ke=["Default","SingleFile","MultipleFiles","ImagesOnly","DocumentsOnly","SmallFileSize","LargeFileSize","Disabled","WithInitialFiles","VideoFiles","SpreadsheetFiles","CustomStyling"];export{_ as CustomStyling,b as Default,C as Disabled,k as DocumentsOnly,S as ImagesOnly,U as LargeFileSize,w as MultipleFiles,N as SingleFile,D as SmallFileSize,V as SpreadsheetFiles,M as VideoFiles,z as WithInitialFiles,Ke as __namedExportsOrder,Pe as default};
