// {
//   "Id": "executor-example-uuid",
//   "Name": "UUID",
//   "Description": "Random UUIDs",
//   "Author": "Executor",
//   "Version": "1.0.0",
//   "TriggerKeywords": ["uuid"],
//   "Commands": [{"Command": "upper", "Description": "Upper case"}]
// }
//
// Example Node.js plugin. Try: uuid    or    uuid upper

const { randomUUID } = require('crypto');

let input = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', chunk => input += chunk);
process.stdin.on('end', () => {
  const request = JSON.parse(input);
  let result = {};
  if (request.method === 'query') {
    const upper = request.params.command === 'upper';
    result.items = [1, 2, 3].map(n => {
      let id = randomUUID();
      if (upper) id = id.toUpperCase();
      return {
        title: id,
        subtitle: 'Enter copies, right-click for more',
        score: 10 - n,
        actions: [
          { id: 'copy-to-clipboard', name: 'Copy', text: id },
          { id: 'executor-paste', name: 'Paste into the previous window', text: id }
        ]
      };
    });
  }
  process.stdout.write(JSON.stringify({ jsonrpc: '2.0', result, id: request.id }));
});
