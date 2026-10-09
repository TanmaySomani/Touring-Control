import { Workbook } from '@oai/artifact-tool';
const wb=Workbook.create();
console.log(wb.help('pivot', {include:'index,examples,notes',maxChars:5500}).ndjson);
