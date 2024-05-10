import removeIcon from "../assets/icons/remove.png";

function getHistory() {
  const item = localStorage.getItem("history");
  return item ? JSON.parse(item) : [];
}

function updateHistory(items) {
  localStorage.setItem("history", JSON.stringify(items.slice(-20)));
}

function addText(newText) {
  const datetime = new Date().toLocaleString([], {
    dateStyle: "short",
    timeStyle: "short",
  });
  const history = getHistory();
  history.unshift([newText, datetime]);
  for (const [i, [text]] of history.slice(1).entries()) {
    if (text === newText) history.splice(i + 1, 1);
  }
  updateHistory(history);
}

function History({ setText, hidden, history, setHistory }) {
  return (
    <div className={"history-container hiddable" + (hidden ? " hidden" : "")}>
      <div className="history">
        {Array.from(history.entries(), ([i, [text, time]]) => (
          <span className="history-item background" key={i}>
            <div
              className="history-text"
              onClick={() => setText(history[i][0])}
            >
              <div>{text}</div>
            </div>
            <div className="history-item-bottom">
              <span className="history-date">{time}</span>
              <img
                className="button"
                onClick={() => {
                  history.splice(i, 1);
                  updateHistory(history);
                  setHistory(getHistory());
                }}
                src={removeIcon}
              ></img>
            </div>
          </span>
        ))}
      </div>
    </div>
  );
}

export { addText, History, getHistory };
