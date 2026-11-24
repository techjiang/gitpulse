const token = process.env.GH_TOKEN;
const id = process.env.ANSWER_ID;
if (!id) throw new Error('ANSWER_ID is required');
const H = { Authorization: 'Bearer ' + token, 'Content-Type': 'application/json', 'User-Agent': 'achievement-trigger' };
async function gql(query, variables) {
  const res = await fetch('https://api.github.com/graphql', {
    method: 'POST',
    headers: H,
    body: JSON.stringify({ query, variables })
  });
  const data = await res.json();
  if (data.errors) throw new Error(JSON.stringify(data.errors));
  return data.data;
}
(async () => {
  await gql(`
    mutation($input: MarkDiscussionCommentAsAnswerInput!) {
      markDiscussionCommentAsAnswer(input: $input) { discussion { id } }
    }`, { input: { id } });
  console.log('accepted=' + id);
})().catch(e => { console.error(e.message); process.exit(1); });
