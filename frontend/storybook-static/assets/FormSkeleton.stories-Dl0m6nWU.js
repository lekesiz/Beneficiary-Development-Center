import{j as e,c as n}from"./utils-BAIen5-9.js";import{S as o}from"./Skeleton-D3sQDuxt.js";import"./index-CleY8y_P.js";import"./_commonjsHelpers-Cpj98o6Y.js";const g=({children:r,className:s,...a})=>e.jsx("div",{className:n("bg-white rounded-lg shadow",s),...a,children:r}),_=({children:r,className:s,...a})=>e.jsx("div",{className:n("px-6 py-4 border-b",s),...a,children:r}),S=({children:r,className:s,as:a="h3",...f})=>e.jsx(a,{className:n("text-lg font-semibold",s),...f,children:r}),w=({children:r,className:s,...a})=>e.jsx("div",{className:n("p-6",s),...a,children:r}),N=({children:r,className:s,...a})=>e.jsx("div",{className:n("px-6 py-4 border-t",s),...a,children:r});try{g.displayName="Card",g.__docgenInfo={description:"",displayName:"Card",props:{}}}catch{}try{_.displayName="CardHeader",_.__docgenInfo={description:"",displayName:"CardHeader",props:{}}}catch{}try{S.displayName="CardTitle",S.__docgenInfo={description:"",displayName:"CardTitle",props:{as:{defaultValue:{value:"h3"},description:"",name:"as",required:!1,type:{name:"enum",value:[{value:"undefined"},{value:'"h1"'},{value:'"h2"'},{value:'"h3"'},{value:'"h4"'},{value:'"h5"'},{value:'"h6"'}]}}}}}catch{}try{w.displayName="CardContent",w.__docgenInfo={description:"",displayName:"CardContent",props:{}}}catch{}try{N.displayName="CardFooter",N.__docgenInfo={description:"",displayName:"CardFooter",props:{}}}catch{}const h=({sections:r=3,fieldsPerSection:s=4,showHeader:a=!0,className:f})=>e.jsxs("div",{className:n("space-y-6",f),children:[a&&e.jsx("div",{className:"flex items-center justify-between",children:e.jsxs("div",{className:"flex items-center space-x-4",children:[e.jsx(o,{className:"h-10 w-32"})," ",e.jsxs("div",{children:[e.jsx(o,{className:"h-8 w-48 mb-2"})," ",e.jsx(o,{className:"h-4 w-64"})," "]})]})}),Array.from({length:r}).map((L,y)=>e.jsxs(g,{className:"p-6",children:[e.jsx(o,{className:"h-6 w-40 mb-4"}),e.jsx("div",{className:"grid grid-cols-1 md:grid-cols-2 gap-4",children:Array.from({length:s}).map((M,x)=>e.jsx("div",{className:x===0?"md:col-span-2":"",children:e.jsxs("div",{className:"space-y-2",children:[e.jsx(o,{className:"h-4 w-24"}),e.jsx(o,{className:"h-10 w-full"})]})},`field-${y}-${x}`))})]},`section-${y}`)),e.jsxs("div",{className:"flex justify-end space-x-4",children:[e.jsx(o,{className:"h-10 w-24"})," ",e.jsx(o,{className:"h-10 w-32"})," "]})]});try{h.displayName="FormSkeleton",h.__docgenInfo={description:"",displayName:"FormSkeleton",props:{sections:{defaultValue:{value:"3"},description:"",name:"sections",required:!1,type:{name:"number | undefined"}},fieldsPerSection:{defaultValue:{value:"4"},description:"",name:"fieldsPerSection",required:!1,type:{name:"number | undefined"}},showHeader:{defaultValue:{value:"true"},description:"",name:"showHeader",required:!1,type:{name:"boolean | undefined"}},className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string | undefined"}}}}}catch{}const Z={title:"Components/FormSkeleton",component:h,parameters:{layout:"padded",docs:{description:{component:"A skeleton loader for forms that displays placeholder content while form data is loading."}}},tags:["autodocs"],argTypes:{sections:{control:{type:"number",min:1,max:5},description:"Number of form sections"},fieldsPerSection:{control:{type:"number",min:1,max:8},description:"Number of fields per section"},showHeader:{control:"boolean",description:"Whether to show the header skeleton"},className:{control:"text",description:"Additional CSS classes"}}},t={args:{sections:3,fieldsPerSection:4,showHeader:!0}},i={args:{sections:1,fieldsPerSection:3,showHeader:!0}},c={args:{sections:5,fieldsPerSection:6,showHeader:!0}},d={args:{sections:2,fieldsPerSection:4,showHeader:!1}},l={name:"Profile Form Example",args:{sections:2,fieldsPerSection:5,showHeader:!0},parameters:{docs:{description:{story:"Example configuration for a user profile form with personal information and settings sections."}}}},m={name:"Registration Form Example",args:{sections:3,fieldsPerSection:4,showHeader:!0},parameters:{docs:{description:{story:"Example configuration for a multi-step registration form with account details, personal info, and preferences."}}}},p={name:"Settings Form Example",args:{sections:4,fieldsPerSection:3,showHeader:!0},parameters:{docs:{description:{story:"Example configuration for an application settings form with multiple configuration sections."}}}},u={name:"Wizard Form Example",args:{sections:1,fieldsPerSection:6,showHeader:!0},parameters:{docs:{description:{story:"Example configuration for a single-step wizard form that loads data dynamically."}}}};var F,j,v;t.parameters={...t.parameters,docs:{...(F=t.parameters)==null?void 0:F.docs,source:{originalSource:`{
  args: {
    sections: 3,
    fieldsPerSection: 4,
    showHeader: true
  }
}`,...(v=(j=t.parameters)==null?void 0:j.docs)==null?void 0:v.source}}};var H,P,C;i.parameters={...i.parameters,docs:{...(H=i.parameters)==null?void 0:H.docs,source:{originalSource:`{
  args: {
    sections: 1,
    fieldsPerSection: 3,
    showHeader: true
  }
}`,...(C=(P=i.parameters)==null?void 0:P.docs)==null?void 0:C.source}}};var E,b,k;c.parameters={...c.parameters,docs:{...(E=c.parameters)==null?void 0:E.docs,source:{originalSource:`{
  args: {
    sections: 5,
    fieldsPerSection: 6,
    showHeader: true
  }
}`,...(k=(b=c.parameters)==null?void 0:b.docs)==null?void 0:k.source}}};var z,q,R;d.parameters={...d.parameters,docs:{...(z=d.parameters)==null?void 0:z.docs,source:{originalSource:`{
  args: {
    sections: 2,
    fieldsPerSection: 4,
    showHeader: false
  }
}`,...(R=(q=d.parameters)==null?void 0:q.docs)==null?void 0:R.source}}};var V,W,A;l.parameters={...l.parameters,docs:{...(V=l.parameters)==null?void 0:V.docs,source:{originalSource:`{
  name: 'Profile Form Example',
  args: {
    sections: 2,
    fieldsPerSection: 5,
    showHeader: true
  },
  parameters: {
    docs: {
      description: {
        story: 'Example configuration for a user profile form with personal information and settings sections.'
      }
    }
  }
}`,...(A=(W=l.parameters)==null?void 0:W.docs)==null?void 0:A.source}}};var I,T,$;m.parameters={...m.parameters,docs:{...(I=m.parameters)==null?void 0:I.docs,source:{originalSource:`{
  name: 'Registration Form Example',
  args: {
    sections: 3,
    fieldsPerSection: 4,
    showHeader: true
  },
  parameters: {
    docs: {
      description: {
        story: 'Example configuration for a multi-step registration form with account details, personal info, and preferences.'
      }
    }
  }
}`,...($=(T=m.parameters)==null?void 0:T.docs)==null?void 0:$.source}}};var D,O,B;p.parameters={...p.parameters,docs:{...(D=p.parameters)==null?void 0:D.docs,source:{originalSource:`{
  name: 'Settings Form Example',
  args: {
    sections: 4,
    fieldsPerSection: 3,
    showHeader: true
  },
  parameters: {
    docs: {
      description: {
        story: 'Example configuration for an application settings form with multiple configuration sections.'
      }
    }
  }
}`,...(B=(O=p.parameters)==null?void 0:O.docs)==null?void 0:B.source}}};var G,J,K;u.parameters={...u.parameters,docs:{...(G=u.parameters)==null?void 0:G.docs,source:{originalSource:`{
  name: 'Wizard Form Example',
  args: {
    sections: 1,
    fieldsPerSection: 6,
    showHeader: true
  },
  parameters: {
    docs: {
      description: {
        story: 'Example configuration for a single-step wizard form that loads data dynamically.'
      }
    }
  }
}`,...(K=(J=u.parameters)==null?void 0:J.docs)==null?void 0:K.source}}};const ee=["Default","SimpleForm","ComplexForm","NoHeader","ProfileForm","RegistrationForm","SettingsForm","WizardForm"];export{c as ComplexForm,t as Default,d as NoHeader,l as ProfileForm,m as RegistrationForm,p as SettingsForm,i as SimpleForm,u as WizardForm,ee as __namedExportsOrder,Z as default};
