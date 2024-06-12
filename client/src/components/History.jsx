import { useState, useEffect } from "react";
import removeIcon from "../assets/icons/remove.png";

function getHistoryData() {
  const item = localStorage.getItem("history");
  return item ? JSON.parse(item) : [];
}

function setHistoryData(items) {
  const previous = getHistoryData();
  localStorage.setItem("history", JSON.stringify(items.slice(-20)));
  const event = new CustomEvent("historyUpdated", {
    detail: { previous: previous },
  });
  window.dispatchEvent(event);
}

function addText(newText) {
  const datetime = new Date().toLocaleString([], {
    dateStyle: "short",
    timeStyle: "short",
  });
  const history = getHistoryData();
  history.unshift([newText, datetime]);
  for (const [i, [text]] of history.slice(1).entries()) {
    if (text === newText) history.splice(i + 1, 1);
  }
  setHistoryData(history);
}

function HistoryItem({ setText, data, removed, index }) {
  const historyData = getHistoryData();
  const [text, date] = data;
  return (
    <span
      className={
        "history-item background hiddable" + (removed ? " hidden" : "")
      }
    >
      <div className="history-text" onClick={() => setText(text)}>
        <div>{text}</div>
      </div>
      <div className="history-item-bottom">
        <span className="history-date">{date}</span>
        <img
          className="button"
          onClick={
            removed
              ? () => {}
              : () => {
                  historyData.splice(index, 1);
                  setHistoryData(historyData);
                }
          }
          src={removeIcon}
        ></img>
      </div>
    </span>
  );
}

function History({ setText, hidden }) {
  const [currentData, setCurrentData] = useState(getHistoryData());
  const [previousData, setPreviousData] = useState(currentData);

  useEffect(() => {
    const handleHistoryUpdate = (event) => {
      setCurrentData(getHistoryData());
      setPreviousData(event.detail.previous);
    };

    window.addEventListener("historyUpdated", handleHistoryUpdate);

    // Cleanup event listener on component unmount
    return () => {
      window.removeEventListener("historyUpdated", handleHistoryUpdate);
    };
  }, []);

  const historyItems = [];
  let wasRemoved = false;
  for (const data of previousData) {
    if (
      !currentData.some(
        (arr) =>
          arr.length === data.length &&
          arr.every((val, index) => val === data[index])
      )
    ) {
      wasRemoved = true;
    }
  }
  if (wasRemoved) {
    let index = 0;
    let key = 0;
    for (const data of previousData) {
      const removed = !currentData.some(
        (arr) =>
          arr.length === data.length &&
          arr.every((val, i) => val === data[i])
      );
      historyItems.push(
        <HistoryItem
          key={key}
          setText={setText}
          data={data}
          removed={removed}
          index={removed ? null : index}
        ></HistoryItem>
      );
      if (!removed) {
        console.log(currentData, data, index)
        index += 1;
      }
      key += 1;
    }
  } else {
    for (let i = 0; i < currentData.length; i++) {
      historyItems.push(
        <HistoryItem
          key={i}
          setText={setText}
          data={currentData[i]}
          removed={false}
          index={i}
        ></HistoryItem>
      );
    }
  }

  return (
    <div className={"history-container hiddable" + (hidden ? " hidden" : "")}>
      <div className="history">{historyItems}</div>
    </div>
  );
}

export { addText, History, getHistoryData, setHistoryData };
