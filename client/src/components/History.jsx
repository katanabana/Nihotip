import { useState, useEffect } from "react";
import removeIcon from "../assets/icons/remove.png";

// Function to retrieve history data from local storage
function getHistoryData() {
  const item = localStorage.getItem("history");
  return item ? JSON.parse(item) : [];
}

// Function to set history data in local storage
function setHistoryData(items) {
  const previous = getHistoryData(); // Retrieve previous history data
  localStorage.setItem("history", JSON.stringify(items.slice(-20))); // Store up to 20 latest items in local storage
  // Dispatch custom event to notify listeners about history update
  const event = new CustomEvent("historyUpdated", {
    detail: { previous: previous },
  });
  window.dispatchEvent(event); // Dispatch the event globally
}

// Function to add new text to history
function addText(newText) {
  const datetime = new Date().toLocaleString([], {
    dateStyle: "short",
    timeStyle: "short",
  });
  let history = getHistoryData(); // Get current history data
  history.unshift([newText, datetime]); // Add new text and timestamp to the beginning of history
  // Remove duplicates of the same text (keeping only the latest entry)
  for (const [i, [text]] of history.slice(1).entries()) {
    if (text === newText) history.splice(i + 1, 1);
  }
  setHistoryData(history); // Update history data in local storage
}

// Component for displaying each history item
function HistoryItem({ setText, data, removed, index }) {
  const historyData = getHistoryData(); // Get current history data
  const [text, date] = data; // Destructure data into text and date

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
          alt=""
          className="button"
          onClick={
            removed
              ? () => {} // No action if item is removed
              : () => {
                  historyData.splice(index, 1); // Remove item from history data
                  setHistoryData(historyData); // Update history data in local storage
                }
          }
          src={removeIcon} // Display remove icon
        ></img>
      </div>
    </span>
  );
}

// Main History component
function History({ setText, hidden }) {
  const [currentData, setCurrentData] = useState(getHistoryData()); // State for current history data
  const [previousData, setPreviousData] = useState(currentData); // State for previous history data

  // Effect to update history data when "historyUpdated" event occurs
  useEffect(() => {
    const handleHistoryUpdate = (event) => {
      setCurrentData(getHistoryData()); // Update current history data
      setPreviousData(event.detail.previous); // Set previous history data from event detail
    };

    window.addEventListener("historyUpdated", handleHistoryUpdate); // Listen for "historyUpdated" event

    // Cleanup event listener on component unmount
    return () => {
      window.removeEventListener("historyUpdated", handleHistoryUpdate); // Remove event listener
    };
  }, []); // Dependency array is empty to run effect only once

  const historyItems = [];
  let wasRemoved = false;

  // Check if any items were removed from previousData
  for (const data of previousData) {
    if (!currentData.some((arr) => arr[0] === data[0])) {
      wasRemoved = true;
      break;
    }
  }

  // Build historyItems array based on whether items were removed or not
  let empty = true;
  if (wasRemoved) {
    let index = 0;
    let key = 0;
    for (const data of previousData) {
      const removed = !currentData.some((arr) => arr[0] === data[0]);
      if (!removed) {
        empty = false;
      }
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
        index += 1;
      }
      key += 1;
    }
  } else {
    for (let i = 0; i < currentData.length; i++) {
      empty = false;
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

  // Render History component with conditional visibility
  return (
    <div
      className={
        "history-container hiddable" + (hidden || empty ? " hidden" : "")
      }
    >
      <div className="history">{historyItems}</div>
    </div>
  );
}

// Exporting functions and component
export { addText, History, getHistoryData, setHistoryData };
