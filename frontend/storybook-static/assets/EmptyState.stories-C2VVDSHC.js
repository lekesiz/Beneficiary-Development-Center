import{j as e,c as L}from"./utils-BAIen5-9.js";import{c as t,B as z}from"./Button--t4ZV3r3.js";import{F as M}from"./file-text-BdmJ-Oca.js";import"./index-CleY8y_P.js";import"./_commonjsHelpers-Cpj98o6Y.js";/**
 * @license lucide-react v0.294.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const O=t("AlertCircle",[["circle",{cx:"12",cy:"12",r:"10",key:"1mglay"}],["line",{x1:"12",x2:"12",y1:"8",y2:"12",key:"1pkeuh"}],["line",{x1:"12",x2:"12.01",y1:"16",y2:"16",key:"4dfq90"}]]);/**
 * @license lucide-react v0.294.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const q=t("BookOpen",[["path",{d:"M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z",key:"vv98re"}],["path",{d:"M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z",key:"1cyq3y"}]]);/**
 * @license lucide-react v0.294.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const V=t("Inbox",[["polyline",{points:"22 12 16 12 14 15 10 15 8 12 2 12",key:"o97t9d"}],["path",{d:"M5.45 5.11 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z",key:"oot6mr"}]]);/**
 * @license lucide-react v0.294.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const P=t("Search",[["circle",{cx:"11",cy:"11",r:"8",key:"4ej97u"}],["path",{d:"m21 21-4.3-4.3",key:"1qie3q"}]]);/**
 * @license lucide-react v0.294.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const H=t("Users",[["path",{d:"M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2",key:"1yyitq"}],["circle",{cx:"9",cy:"7",r:"4",key:"nufk8"}],["path",{d:"M22 21v-2a4 4 0 0 0-3-3.87",key:"kshegd"}],["path",{d:"M16 3.13a4 4 0 0 1 0 7.75",key:"1da9ce"}]]),d=({icon:p,title:_,description:B,action:u,className:G})=>e.jsxs("div",{className:L("flex flex-col items-center justify-center py-12 px-4",G),children:[e.jsx("div",{className:"bg-gray-100 rounded-full p-4 mb-4",children:e.jsx(p,{className:"h-12 w-12 text-gray-400"})}),e.jsx("h3",{className:"text-lg font-semibold text-gray-900 mb-2 text-center",children:_}),e.jsx("p",{className:"text-gray-600 text-center max-w-md mb-6",children:B}),u&&e.jsx(z,{onClick:u.onClick,size:"lg",children:u.text})]});d.displayName="EmptyState";try{d.displayName="EmptyState",d.__docgenInfo={description:"",displayName:"EmptyState",props:{icon:{defaultValue:null,description:"",name:"icon",required:!0,type:{name:"LucideIcon"}},title:{defaultValue:null,description:"",name:"title",required:!0,type:{name:"string"}},description:{defaultValue:null,description:"",name:"description",required:!0,type:{name:"string"}},action:{defaultValue:null,description:"",name:"action",required:!1,type:{name:"{ text: string; onClick: () => void; } | undefined"}},className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string | undefined"}}}}}catch{}const $={title:"UI/EmptyState",component:d,parameters:{layout:"centered"},tags:["autodocs"],argTypes:{icon:{control:!1,description:"Lucide React icon component to display"},title:{control:"text",description:"Main heading text"},description:{control:"text",description:"Descriptive text explaining the empty state"},action:{control:!1,description:"Optional action button configuration"}}},o={args:{icon:M,title:"No Documents Found",description:"Upload your first document to get started. You can upload PDFs, Word documents, and more.",action:{text:"Upload Document",onClick:()=>console.log("Upload clicked")}}},r={args:{icon:V,title:"Your Inbox is Empty",description:"When you receive new messages or notifications, they will appear here."}},n={args:{icon:H,title:"No Team Members",description:"Invite team members to collaborate on your projects and share insights.",action:{text:"Invite Team Members",onClick:()=>console.log("Invite clicked")}}},a={args:{icon:q,title:"No Courses Available",description:"Create your first course to start delivering engaging learning experiences.",action:{text:"Create Course",onClick:()=>console.log("Create course clicked")}}},i={args:{icon:P,title:"No Results Found",description:"Try adjusting your search terms or filters to find what you're looking for.",action:{text:"Clear Search",onClick:()=>console.log("Clear search clicked")}}},s={args:{icon:O,title:"Something Went Wrong",description:"We encountered an error while loading this content. Please try again later.",action:{text:"Try Again",onClick:()=>console.log("Retry clicked")}}},c={args:{icon:M,title:"No Reports Generated",description:"Generate your first report to gain insights into your data.",action:{text:"Generate Report",onClick:()=>console.log("Generate clicked")},className:"bg-blue-50 rounded-lg p-8"}},l={args:{icon:q,title:"Welcome to Your Library",description:"Your personal library is empty right now. Start by adding books, articles, or documents that interest you. You can organize them into collections, add tags for easy searching, and even share them with others. Building your library helps you keep track of your learning journey and reference materials.",action:{text:"Add Your First Item",onClick:()=>console.log("Add item clicked")}}};var m,g,y;o.parameters={...o.parameters,docs:{...(m=o.parameters)==null?void 0:m.docs,source:{originalSource:`{
  args: {
    icon: FileText,
    title: 'No Documents Found',
    description: 'Upload your first document to get started. You can upload PDFs, Word documents, and more.',
    action: {
      text: 'Upload Document',
      onClick: () => console.log('Upload clicked')
    }
  }
}`,...(y=(g=o.parameters)==null?void 0:g.docs)==null?void 0:y.source}}};var h,k,x;r.parameters={...r.parameters,docs:{...(h=r.parameters)==null?void 0:h.docs,source:{originalSource:`{
  args: {
    icon: Inbox,
    title: 'Your Inbox is Empty',
    description: 'When you receive new messages or notifications, they will appear here.'
  }
}`,...(x=(k=r.parameters)==null?void 0:k.docs)==null?void 0:x.source}}};var f,C,b;n.parameters={...n.parameters,docs:{...(f=n.parameters)==null?void 0:f.docs,source:{originalSource:`{
  args: {
    icon: Users,
    title: 'No Team Members',
    description: 'Invite team members to collaborate on your projects and share insights.',
    action: {
      text: 'Invite Team Members',
      onClick: () => console.log('Invite clicked')
    }
  }
}`,...(b=(C=n.parameters)==null?void 0:C.docs)==null?void 0:b.source}}};var N,S,v;a.parameters={...a.parameters,docs:{...(N=a.parameters)==null?void 0:N.docs,source:{originalSource:`{
  args: {
    icon: BookOpen,
    title: 'No Courses Available',
    description: 'Create your first course to start delivering engaging learning experiences.',
    action: {
      text: 'Create Course',
      onClick: () => console.log('Create course clicked')
    }
  }
}`,...(v=(S=a.parameters)==null?void 0:S.docs)==null?void 0:v.source}}};var I,j,w;i.parameters={...i.parameters,docs:{...(I=i.parameters)==null?void 0:I.docs,source:{originalSource:`{
  args: {
    icon: Search,
    title: 'No Results Found',
    description: 'Try adjusting your search terms or filters to find what you\\'re looking for.',
    action: {
      text: 'Clear Search',
      onClick: () => console.log('Clear search clicked')
    }
  }
}`,...(w=(j=i.parameters)==null?void 0:j.docs)==null?void 0:w.source}}};var A,W,F;s.parameters={...s.parameters,docs:{...(A=s.parameters)==null?void 0:A.docs,source:{originalSource:`{
  args: {
    icon: AlertCircle,
    title: 'Something Went Wrong',
    description: 'We encountered an error while loading this content. Please try again later.',
    action: {
      text: 'Try Again',
      onClick: () => console.log('Retry clicked')
    }
  }
}`,...(F=(W=s.parameters)==null?void 0:W.docs)==null?void 0:F.source}}};var R,T,U;c.parameters={...c.parameters,docs:{...(R=c.parameters)==null?void 0:R.docs,source:{originalSource:`{
  args: {
    icon: FileText,
    title: 'No Reports Generated',
    description: 'Generate your first report to gain insights into your data.',
    action: {
      text: 'Generate Report',
      onClick: () => console.log('Generate clicked')
    },
    className: 'bg-blue-50 rounded-lg p-8'
  }
}`,...(U=(T=c.parameters)==null?void 0:T.docs)==null?void 0:U.source}}};var Y,D,E;l.parameters={...l.parameters,docs:{...(Y=l.parameters)==null?void 0:Y.docs,source:{originalSource:`{
  args: {
    icon: BookOpen,
    title: 'Welcome to Your Library',
    description: 'Your personal library is empty right now. Start by adding books, articles, or documents that interest you. You can organize them into collections, add tags for easy searching, and even share them with others. Building your library helps you keep track of your learning journey and reference materials.',
    action: {
      text: 'Add Your First Item',
      onClick: () => console.log('Add item clicked')
    }
  }
}`,...(E=(D=l.parameters)==null?void 0:D.docs)==null?void 0:E.source}}};const ee=["Default","WithoutAction","NoUsers","NoCourses","NoSearchResults","ErrorState","CustomStyling","LongDescription"];export{c as CustomStyling,o as Default,s as ErrorState,l as LongDescription,a as NoCourses,i as NoSearchResults,n as NoUsers,r as WithoutAction,ee as __namedExportsOrder,$ as default};
