/* xlsx.js (C) 2013-present SheetJS -- http://sheetjs.com */
importScripts('/static/backend/js/sheetjs/shim.js' );
importScripts('/static/backend/js/sheetjs/xlsx.full.min.js' );
postMessage({t:"ready"});

onmessage = function (evt) {
  var v;
  try {
    v = XLSX.read(evt.data.d, {type: evt.data.b});
    postMessage({t:"xlsx", d:JSON.stringify(v)});
  } catch(e) {
    postMessage({t:"e",d:e.stack||e});
  }
};
