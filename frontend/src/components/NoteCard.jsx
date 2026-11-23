function NoteCard({ item }) {
  return (
    <li>
      <h3>{item.title}</h3>
      <p>{item.content}</p>
      <p>Date : {item.created_at}</p>
    </li>
  );
}

export default NoteCard;
