import{j as e,c as H}from"./utils-BAIen5-9.js";import{S as a}from"./Skeleton-D3sQDuxt.js";import"./index-CleY8y_P.js";import"./_commonjsHelpers-Cpj98o6Y.js";const g=({columns:s=5,rows:W=10,showPagination:z=!0,className:B})=>e.jsxs("div",{className:H("w-full",B),children:[e.jsx("div",{className:"rounded-md border",children:e.jsx("div",{className:"overflow-hidden",children:e.jsxs("table",{className:"w-full",children:[e.jsx("thead",{className:"border-b bg-gray-50 dark:bg-gray-800",children:e.jsx("tr",{children:Array.from({length:s}).map((G,r)=>e.jsx("th",{className:"px-6 py-3 text-left",children:e.jsx(a,{className:"h-4 w-24"})},`header-${r}`))})}),e.jsx("tbody",{children:Array.from({length:W}).map((G,r)=>e.jsx("tr",{className:"border-b transition-colors hover:bg-gray-50/50 dark:hover:bg-gray-800/50",children:Array.from({length:s}).map((J,o)=>e.jsx("td",{className:"px-6 py-4",children:o===0?e.jsxs("div",{className:"space-y-2",children:[e.jsx(a,{className:"h-4 w-32"}),e.jsx(a,{className:"h-3 w-24"})]}):o===s-1?e.jsxs("div",{className:"flex items-center space-x-2",children:[e.jsx(a,{className:"h-8 w-8 rounded"}),e.jsx(a,{className:"h-8 w-8 rounded"}),e.jsx(a,{className:"h-8 w-8 rounded"})]}):o===1?e.jsx(a,{className:"h-6 w-20 rounded-full"}):e.jsx(a,{className:"h-4 w-28"})},`cell-${r}-${o}`))},`row-${r}`))})]})})}),z&&e.jsxs("div",{className:"flex items-center justify-between px-2 py-4",children:[e.jsx("div",{className:"flex items-center space-x-2",children:e.jsx(a,{className:"h-4 w-32"})}),e.jsxs("div",{className:"flex items-center space-x-2",children:[e.jsx(a,{className:"h-8 w-20 rounded"}),e.jsx(a,{className:"h-8 w-8 rounded"}),e.jsx(a,{className:"h-8 w-8 rounded"}),e.jsx(a,{className:"h-8 w-8 rounded"}),e.jsx(a,{className:"h-8 w-8 rounded"}),e.jsx(a,{className:"h-8 w-20 rounded"})]})]})]});try{g.displayName="DataTableSkeleton",g.__docgenInfo={description:"",displayName:"DataTableSkeleton",props:{columns:{defaultValue:{value:"5"},description:"",name:"columns",required:!1,type:{name:"number | undefined"}},rows:{defaultValue:{value:"10"},description:"",name:"rows",required:!1,type:{name:"number | undefined"}},showPagination:{defaultValue:{value:"true"},description:"",name:"showPagination",required:!1,type:{name:"boolean | undefined"}},className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string | undefined"}}}}}catch{}const Z={title:"Components/DataTableSkeleton",component:g,parameters:{layout:"padded",docs:{description:{component:"A skeleton loader that mimics the structure of a data table, providing visual feedback while data is loading."}}},tags:["autodocs"],argTypes:{columns:{control:{type:"number",min:1,max:10},description:"Number of columns to display"},rows:{control:{type:"number",min:1,max:20},description:"Number of rows to display"},showPagination:{control:"boolean",description:"Whether to show pagination skeleton"},className:{control:"text",description:"Additional CSS classes"}}},n={args:{columns:5,rows:10,showPagination:!0}},t={args:{columns:3,rows:8,showPagination:!0}},c={args:{columns:8,rows:10,showPagination:!0}},l={args:{columns:5,rows:3,showPagination:!1}},i={args:{columns:5,rows:10,showPagination:!1}},m={args:{columns:4,rows:5,showPagination:!1}},d={args:{columns:10,rows:20,showPagination:!0}},u={name:"User Table Example",args:{columns:6,rows:10,showPagination:!0},parameters:{docs:{description:{story:"Example configuration for a typical user management table with columns for name, email, role, status, created date, and actions."}}}},p={name:"Product Table Example",args:{columns:7,rows:12,showPagination:!0},parameters:{docs:{description:{story:"Example configuration for a product listing table with columns for image, name, category, price, stock, status, and actions."}}}};var w,h,f;n.parameters={...n.parameters,docs:{...(w=n.parameters)==null?void 0:w.docs,source:{originalSource:`{
  args: {
    columns: 5,
    rows: 10,
    showPagination: true
  }
}`,...(f=(h=n.parameters)==null?void 0:h.docs)==null?void 0:f.source}}};var x,b,y;t.parameters={...t.parameters,docs:{...(x=t.parameters)==null?void 0:x.docs,source:{originalSource:`{
  args: {
    columns: 3,
    rows: 8,
    showPagination: true
  }
}`,...(y=(b=t.parameters)==null?void 0:b.docs)==null?void 0:y.source}}};var N,j,P;c.parameters={...c.parameters,docs:{...(N=c.parameters)==null?void 0:N.docs,source:{originalSource:`{
  args: {
    columns: 8,
    rows: 10,
    showPagination: true
  }
}`,...(P=(j=c.parameters)==null?void 0:j.docs)==null?void 0:P.source}}};var S,T,v;l.parameters={...l.parameters,docs:{...(S=l.parameters)==null?void 0:S.docs,source:{originalSource:`{
  args: {
    columns: 5,
    rows: 3,
    showPagination: false
  }
}`,...(v=(T=l.parameters)==null?void 0:T.docs)==null?void 0:v.source}}};var _,k,E;i.parameters={...i.parameters,docs:{...(_=i.parameters)==null?void 0:_.docs,source:{originalSource:`{
  args: {
    columns: 5,
    rows: 10,
    showPagination: false
  }
}`,...(E=(k=i.parameters)==null?void 0:k.docs)==null?void 0:E.source}}};var C,D,A;m.parameters={...m.parameters,docs:{...(C=m.parameters)==null?void 0:C.docs,source:{originalSource:`{
  args: {
    columns: 4,
    rows: 5,
    showPagination: false
  }
}`,...(A=(D=m.parameters)==null?void 0:D.docs)==null?void 0:A.source}}};var q,F,U;d.parameters={...d.parameters,docs:{...(q=d.parameters)==null?void 0:q.docs,source:{originalSource:`{
  args: {
    columns: 10,
    rows: 20,
    showPagination: true
  }
}`,...(U=(F=d.parameters)==null?void 0:F.docs)==null?void 0:U.source}}};var V,$,R;u.parameters={...u.parameters,docs:{...(V=u.parameters)==null?void 0:V.docs,source:{originalSource:`{
  name: 'User Table Example',
  args: {
    columns: 6,
    rows: 10,
    showPagination: true
  },
  parameters: {
    docs: {
      description: {
        story: 'Example configuration for a typical user management table with columns for name, email, role, status, created date, and actions.'
      }
    }
  }
}`,...(R=($=u.parameters)==null?void 0:$.docs)==null?void 0:R.source}}};var L,M,O;p.parameters={...p.parameters,docs:{...(L=p.parameters)==null?void 0:L.docs,source:{originalSource:`{
  name: 'Product Table Example',
  args: {
    columns: 7,
    rows: 12,
    showPagination: true
  },
  parameters: {
    docs: {
      description: {
        story: 'Example configuration for a product listing table with columns for image, name, category, price, stock, status, and actions.'
      }
    }
  }
}`,...(O=(M=p.parameters)==null?void 0:M.docs)==null?void 0:O.source}}};const I=["Default","FewColumns","ManyColumns","FewRows","NoPagination","CompactTable","LargeTable","UserTable","ProductTable"];export{m as CompactTable,n as Default,t as FewColumns,l as FewRows,d as LargeTable,c as ManyColumns,i as NoPagination,p as ProductTable,u as UserTable,I as __namedExportsOrder,Z as default};
