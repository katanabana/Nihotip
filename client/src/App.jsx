import { useState, useEffect } from "react";
import process from "process";
import { Unit } from "./components/Unit.jsx";
import Menu from "./components/Menu.jsx";
import { addText, History } from "./components/History.jsx";
import editIcon from "./assets/icons/edit.png";
import displayIcon from "./assets/icons/display.png";
import loaderIcon from "./assets/icons/loader.png";
import settingsIcon from "./assets/icons/settings.png";

async function getTokens(text) {
  let url = process.env.REACT_APP_API_URL;
  url += "/tokens?text=";
  url += text.replaceAll("\n", "%0A");
  const respnose = await fetch(url, { mode: "cors" });
  return await respnose.json();
}

function App() {
  const [text, setText] = useState("");
  const [tokens, setTokens] = useState([]);
  const [beingEdited, setBeingEdited] = useState(true);
  const [color, setColor] = useState("part of speech");
  const [currentText, setCurrentText] = useState(false);
  const [loading, setLoading] = useState(false);
  const [hidden, setHidden] = useState(true);

  const maxText = 2000;

  useEffect(() => {
    if (beingEdited) return;
    setLoading(true);
    getTokens(text).then((tokens) => {
      setTokens(tokens);
      setLoading(false);
      addText(text);
    });
  }, [text]);

  const textComponent = beingEdited ? (
    <div
      className="input"
      contentEditable="plaintext-only"
      suppressContentEditableWarning={true}
      onInput={(event) => setCurrentText(event.target.innerText)}
      /* onInput shouldn't invoke setText(event.target.innerText) because text is content of event.target*/
    >
      {text}
    </div>
  ) : (
    <div className="display">
      {Array.from(tokens.entries(), ([i, token]) => {
        return <Unit key={i} token={token} color={color} zIndex={1000}></Unit>;
      })}
    </div>
  );

  function changeMode() {
    if (beingEdited && currentText !== text) {
      setText(currentText);
      setTokens([currentText]);
    }
    if (!beingEdited) setLoading(false);
    setBeingEdited(!beingEdited);
    setText(currentText);
  }

  const mode = (
    <div
      className={
        "mode hiddable" +
        (0 < currentText.length && currentText.length <= maxText
          ? ""
          : " hidden")
      }
    >
      <img
        className="button"
        src={beingEdited ? displayIcon : editIcon}
        onClick={changeMode}
      ></img>
    </div>
  );

  const wordCount = (
    <div
      className={
        "word-count hiddable" +
        (currentText.length >= 0.75 * maxText && beingEdited ? "" : " hidden") +
        (currentText.length > maxText ? " overflow" : "")
      }
    >
      {`${currentText.length} / ${maxText}`}
    </div>
  );

  return (
    <>
      <div id="tooltips"></div>
      <Menu
        color={color}
        setColor={setColor}
        loading={loading}
        beingEdited={beingEdited}
        hidden={hidden}
      ></Menu>
      <div className="text-container">
        {wordCount}
        <div className={"background text" + (loading ? " blur" : "")}>
          {textComponent}
          <img
            className={"loader hiddable" + (loading ? "" : " hidden")}
            src={loaderIcon}
          ></img>
        </div>
        <nav>
          <img
            className={
              "settings button hiddable" +
              (beingEdited || loading ? " hidden" : "")
            }
            onClick={() => setHidden(!hidden)}
            src={settingsIcon}
          ></img>
          {mode}
        </nav>
      </div>
      <History
        setText={(text) => {
          document.getElementsByClassName("input")[0].innerHTML = text;
          setCurrentText(text);
        }}
        hidden={currentText || history.length === 0}
      ></History>
    </>
  );
}

export default App;
