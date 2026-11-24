const token = process.env.GH_TOKEN;
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
  const info = await gql(`
    query {
      repository(owner: "techjiang", name: "gitpulse") {
        id
        discussionCategories(first: 10) { nodes { id name isAnswerable } }
      }
    }`);
  const cat = info.repository.discussionCategories.nodes.find(c => c.isAnswerable);
  if (!cat) throw new Error('No answerable category');
  const created = [];
  for (let i = 1; i <= 6; i++) {
    const d = await gql(`
      mutation($input: CreateDiscussionInput!) {
        createDiscussion(input: $input) { discussion { id number } }
      }`, {
        input: {
          repositoryId: info.repository.id,
          categoryId: cat.id,
          title: 'gitpulse usage question ' + Date.now() + '-' + i,
          body: 'Project Q&A ' + i + ': how would you use gitpulse in a weekly engineering digest?'
        }
      });
    created.push({ id: d.createDiscussion.discussion.id, number: d.createDiscussion.discussion.number });
    console.log('DISCUSSION_ID=' + d.createDiscussion.discussion.id);
    console.log('DISCUSSION_NUMBER=' + d.createDiscussion.discussion.number);
  }
  console.log('CREATED_COUNT=' + created.length);
})().catch(e => { console.error(e.message); process.exit(1); });
