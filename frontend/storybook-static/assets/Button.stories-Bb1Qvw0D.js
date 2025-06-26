import{j as r}from"./utils-BAIen5-9.js";import{c as n,B as e}from"./Button--t4ZV3r3.js";import"./index-CleY8y_P.js";import"./_commonjsHelpers-Cpj98o6Y.js";/**
 * @license lucide-react v0.294.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const jr=n("Download",[["path",{d:"M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4",key:"ih7n3h"}],["polyline",{points:"7 10 12 15 17 10",key:"2ggqvy"}],["line",{x1:"12",x2:"12",y1:"15",y2:"3",key:"1vk2je"}]]);/**
 * @license lucide-react v0.294.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const kr=n("Eye",[["path",{d:"M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z",key:"rwhkz3"}],["circle",{cx:"12",cy:"12",r:"3",key:"1v7zrd"}]]);/**
 * @license lucide-react v0.294.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Lr=n("PenSquare",[["path",{d:"M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7",key:"1qinfi"}],["path",{d:"M18.5 2.5a2.12 2.12 0 0 1 3 3L12 15l-4 1 1-4Z",key:"w2jsv5"}]]);/**
 * @license lucide-react v0.294.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Sr=n("Plus",[["path",{d:"M5 12h14",key:"1ays0h"}],["path",{d:"M12 5v14",key:"s699le"}]]);/**
 * @license lucide-react v0.294.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const fr=n("Trash2",[["path",{d:"M3 6h18",key:"d0wm0j"}],["path",{d:"M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6",key:"4alrt4"}],["path",{d:"M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2",key:"v07s0e"}],["line",{x1:"10",x2:"10",y1:"11",y2:"17",key:"1uufr5"}],["line",{x1:"14",x2:"14",y1:"11",y2:"17",key:"xtxkd"}]]),Pr={title:"UI/Button",component:e,parameters:{layout:"centered",docs:{description:{component:"Uygulamada kullanılan temel buton bileşeni. Farklı varyantlar, boyutlar ve durumları destekler."}}},tags:["autodocs"],argTypes:{variant:{control:"select",options:["primary","secondary","danger","success","warning","ghost","outline","link"],description:"Butonun görsel stili"},size:{control:"select",options:["xs","sm","md","lg","xl"],description:"Butonun boyutu"},loading:{control:"boolean",description:"Yüklenme durumunu gösterir"},disabled:{control:"boolean",description:"Butonu devre dışı bırakır"},loadingText:{control:"text",description:"Yüklenme sırasında gösterilecek metin"}}},a={args:{children:"Primary Button",variant:"primary",size:"md"}},t={args:{children:"Secondary Button",variant:"secondary",size:"md"}},s={args:{children:"Delete Item",variant:"danger",size:"md"}},i={args:{children:"Save Changes",variant:"success",size:"md"}},o={args:{children:"Warning Action",variant:"warning",size:"md"}},c={args:{children:"Ghost Button",variant:"ghost",size:"md"}},d={args:{children:"Outline Button",variant:"outline",size:"md"}},l={args:{children:"Link Button",variant:"link",size:"md"}},m={args:{children:"Loading Button",variant:"primary",size:"md",loading:!0}},u={args:{children:"Save Data",variant:"primary",size:"md",loading:!0,loadingText:"Kayıt ediliyor..."}},g={args:{children:"Disabled Button",variant:"primary",size:"md",disabled:!0}},p={args:{children:"Yeni Ekle",variant:"primary",size:"md",leftIcon:r.jsx(Sr,{size:16})}},v={args:{children:"İndir",variant:"secondary",size:"md",rightIcon:r.jsx(jr,{size:16})}},h={render:()=>r.jsxs("div",{className:"flex items-center gap-4 flex-wrap",children:[r.jsx(e,{size:"xs",variant:"primary",children:"Extra Small"}),r.jsx(e,{size:"sm",variant:"primary",children:"Small"}),r.jsx(e,{size:"md",variant:"primary",children:"Medium"}),r.jsx(e,{size:"lg",variant:"primary",children:"Large"}),r.jsx(e,{size:"xl",variant:"primary",children:"Extra Large"})]})},y={render:()=>r.jsxs("div",{className:"grid grid-cols-2 gap-4 max-w-md",children:[r.jsx(e,{variant:"primary",children:"Primary"}),r.jsx(e,{variant:"secondary",children:"Secondary"}),r.jsx(e,{variant:"danger",children:"Danger"}),r.jsx(e,{variant:"success",children:"Success"}),r.jsx(e,{variant:"warning",children:"Warning"}),r.jsx(e,{variant:"ghost",children:"Ghost"}),r.jsx(e,{variant:"outline",children:"Outline"}),r.jsx(e,{variant:"link",children:"Link"})]})},x={render:()=>r.jsxs("div",{className:"flex items-center gap-2",children:[r.jsx(e,{variant:"primary",size:"sm",leftIcon:r.jsx(Sr,{size:14}),children:"Yeni"}),r.jsx(e,{variant:"ghost",size:"sm",children:r.jsx(Lr,{size:14})}),r.jsx(e,{variant:"ghost",size:"sm",children:r.jsx(kr,{size:14})}),r.jsx(e,{variant:"ghost",size:"sm",className:"text-red-600 hover:text-red-800",children:r.jsx(fr,{size:14})})]})},B={render:()=>r.jsxs("div",{className:"flex items-center justify-end gap-3",children:[r.jsx(e,{variant:"outline",children:"İptal"}),r.jsx(e,{variant:"primary",children:"Kaydet"})]})},z={render:()=>r.jsxs("div",{className:"flex items-center gap-4 flex-wrap",children:[r.jsx(e,{variant:"primary",loading:!0,children:"Primary Loading"}),r.jsx(e,{variant:"secondary",loading:!0,children:"Secondary Loading"}),r.jsx(e,{variant:"danger",loading:!0,loadingText:"Siliniyor...",children:"Delete Loading"}),r.jsx(e,{variant:"success",loading:!0,loadingText:"Kaydediliyor...",children:"Save Loading"})]})};var S,j,k;a.parameters={...a.parameters,docs:{...(S=a.parameters)==null?void 0:S.docs,source:{originalSource:`{
  args: {
    children: 'Primary Button',
    variant: 'primary',
    size: 'md'
  }
}`,...(k=(j=a.parameters)==null?void 0:j.docs)==null?void 0:k.source}}};var L,f,w;t.parameters={...t.parameters,docs:{...(L=t.parameters)==null?void 0:L.docs,source:{originalSource:`{
  args: {
    children: 'Secondary Button',
    variant: 'secondary',
    size: 'md'
  }
}`,...(w=(f=t.parameters)==null?void 0:f.docs)==null?void 0:w.source}}};var D,b,I;s.parameters={...s.parameters,docs:{...(D=s.parameters)==null?void 0:D.docs,source:{originalSource:`{
  args: {
    children: 'Delete Item',
    variant: 'danger',
    size: 'md'
  }
}`,...(I=(b=s.parameters)==null?void 0:b.docs)==null?void 0:I.source}}};var P,T,E;i.parameters={...i.parameters,docs:{...(P=i.parameters)==null?void 0:P.docs,source:{originalSource:`{
  args: {
    children: 'Save Changes',
    variant: 'success',
    size: 'md'
  }
}`,...(E=(T=i.parameters)==null?void 0:T.docs)==null?void 0:E.source}}};var N,W,M;o.parameters={...o.parameters,docs:{...(N=o.parameters)==null?void 0:N.docs,source:{originalSource:`{
  args: {
    children: 'Warning Action',
    variant: 'warning',
    size: 'md'
  }
}`,...(M=(W=o.parameters)==null?void 0:W.docs)==null?void 0:M.source}}};var O,A,G;c.parameters={...c.parameters,docs:{...(O=c.parameters)==null?void 0:O.docs,source:{originalSource:`{
  args: {
    children: 'Ghost Button',
    variant: 'ghost',
    size: 'md'
  }
}`,...(G=(A=c.parameters)==null?void 0:A.docs)==null?void 0:G.source}}};var K,V,Y;d.parameters={...d.parameters,docs:{...(K=d.parameters)==null?void 0:K.docs,source:{originalSource:`{
  args: {
    children: 'Outline Button',
    variant: 'outline',
    size: 'md'
  }
}`,...(Y=(V=d.parameters)==null?void 0:V.docs)==null?void 0:Y.source}}};var q,C,F;l.parameters={...l.parameters,docs:{...(q=l.parameters)==null?void 0:q.docs,source:{originalSource:`{
  args: {
    children: 'Link Button',
    variant: 'link',
    size: 'md'
  }
}`,...(F=(C=l.parameters)==null?void 0:C.docs)==null?void 0:F.source}}};var H,R,U;m.parameters={...m.parameters,docs:{...(H=m.parameters)==null?void 0:H.docs,source:{originalSource:`{
  args: {
    children: 'Loading Button',
    variant: 'primary',
    size: 'md',
    loading: true
  }
}`,...(U=(R=m.parameters)==null?void 0:R.docs)==null?void 0:U.source}}};var Z,_,J;u.parameters={...u.parameters,docs:{...(Z=u.parameters)==null?void 0:Z.docs,source:{originalSource:`{
  args: {
    children: 'Save Data',
    variant: 'primary',
    size: 'md',
    loading: true,
    loadingText: 'Kayıt ediliyor...'
  }
}`,...(J=(_=u.parameters)==null?void 0:_.docs)==null?void 0:J.source}}};var Q,X,$;g.parameters={...g.parameters,docs:{...(Q=g.parameters)==null?void 0:Q.docs,source:{originalSource:`{
  args: {
    children: 'Disabled Button',
    variant: 'primary',
    size: 'md',
    disabled: true
  }
}`,...($=(X=g.parameters)==null?void 0:X.docs)==null?void 0:$.source}}};var rr,er,nr;p.parameters={...p.parameters,docs:{...(rr=p.parameters)==null?void 0:rr.docs,source:{originalSource:`{
  args: {
    children: 'Yeni Ekle',
    variant: 'primary',
    size: 'md',
    leftIcon: <Plus size={16} />
  }
}`,...(nr=(er=p.parameters)==null?void 0:er.docs)==null?void 0:nr.source}}};var ar,tr,sr;v.parameters={...v.parameters,docs:{...(ar=v.parameters)==null?void 0:ar.docs,source:{originalSource:`{
  args: {
    children: 'İndir',
    variant: 'secondary',
    size: 'md',
    rightIcon: <Download size={16} />
  }
}`,...(sr=(tr=v.parameters)==null?void 0:tr.docs)==null?void 0:sr.source}}};var ir,or,cr;h.parameters={...h.parameters,docs:{...(ir=h.parameters)==null?void 0:ir.docs,source:{originalSource:`{
  render: () => <div className="flex items-center gap-4 flex-wrap">
      <Button size="xs" variant="primary">
        Extra Small
      </Button>
      <Button size="sm" variant="primary">
        Small
      </Button>
      <Button size="md" variant="primary">
        Medium
      </Button>
      <Button size="lg" variant="primary">
        Large
      </Button>
      <Button size="xl" variant="primary">
        Extra Large
      </Button>
    </div>
}`,...(cr=(or=h.parameters)==null?void 0:or.docs)==null?void 0:cr.source}}};var dr,lr,mr;y.parameters={...y.parameters,docs:{...(dr=y.parameters)==null?void 0:dr.docs,source:{originalSource:`{
  render: () => <div className="grid grid-cols-2 gap-4 max-w-md">
      <Button variant="primary">Primary</Button>
      <Button variant="secondary">Secondary</Button>
      <Button variant="danger">Danger</Button>
      <Button variant="success">Success</Button>
      <Button variant="warning">Warning</Button>
      <Button variant="ghost">Ghost</Button>
      <Button variant="outline">Outline</Button>
      <Button variant="link">Link</Button>
    </div>
}`,...(mr=(lr=y.parameters)==null?void 0:lr.docs)==null?void 0:mr.source}}};var ur,gr,pr;x.parameters={...x.parameters,docs:{...(ur=x.parameters)==null?void 0:ur.docs,source:{originalSource:`{
  render: () => <div className="flex items-center gap-2">
      <Button variant="primary" size="sm" leftIcon={<Plus size={14} />}>
        Yeni
      </Button>
      <Button variant="ghost" size="sm">
        <Edit size={14} />
      </Button>
      <Button variant="ghost" size="sm">
        <Eye size={14} />
      </Button>
      <Button variant="ghost" size="sm" className="text-red-600 hover:text-red-800">
        <Trash2 size={14} />
      </Button>
    </div>
}`,...(pr=(gr=x.parameters)==null?void 0:gr.docs)==null?void 0:pr.source}}};var vr,hr,yr;B.parameters={...B.parameters,docs:{...(vr=B.parameters)==null?void 0:vr.docs,source:{originalSource:`{
  render: () => <div className="flex items-center justify-end gap-3">
      <Button variant="outline">İptal</Button>
      <Button variant="primary">Kaydet</Button>
    </div>
}`,...(yr=(hr=B.parameters)==null?void 0:hr.docs)==null?void 0:yr.source}}};var xr,Br,zr;z.parameters={...z.parameters,docs:{...(xr=z.parameters)==null?void 0:xr.docs,source:{originalSource:`{
  render: () => <div className="flex items-center gap-4 flex-wrap">
      <Button variant="primary" loading>
        Primary Loading
      </Button>
      <Button variant="secondary" loading>
        Secondary Loading
      </Button>
      <Button variant="danger" loading loadingText="Siliniyor...">
        Delete Loading
      </Button>
      <Button variant="success" loading loadingText="Kaydediliyor...">
        Save Loading
      </Button>
    </div>
}`,...(zr=(Br=z.parameters)==null?void 0:Br.docs)==null?void 0:zr.source}}};const Tr=["Primary","Secondary","Danger","Success","Warning","Ghost","Outline","Link","Loading","LoadingWithCustomText","Disabled","WithLeftIcon","WithRightIcon","SizeVariations","AllVariants","ActionButtons","FormButtons","LoadingStates"];export{x as ActionButtons,y as AllVariants,s as Danger,g as Disabled,B as FormButtons,c as Ghost,l as Link,m as Loading,z as LoadingStates,u as LoadingWithCustomText,d as Outline,a as Primary,t as Secondary,h as SizeVariations,i as Success,o as Warning,p as WithLeftIcon,v as WithRightIcon,Tr as __namedExportsOrder,Pr as default};
