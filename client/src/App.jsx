import { useState, useEffect } from "react";
import Units from "./components/Unit.jsx";

function App() {
  // displaying parameters:
  const [showColor, setShowColor] = useState(true);

  // main element is element for displaying/editing text (presumably japanese)
  // user can see tooltips when they move cursor on the text inside a display element
  // inside an input element user can edit text for which they want to get tooltips for

  const [showDisplay, setShowDisplay] = useState(true);
  const [text, setText] = useState("");
  // when showDisplay is true the returned element is a display element
  // when showDisplay is false the returned element is an input element

  useEffect(() => {
    // move caret to the input element after its creation and select the entire text in the input element
    // selecting the entire text allows user to quickly delete it or replace it with another text right after clicking on the display
    const input = document.getElementById("input");
    if (input) {
      const range = document.createRange();
      range.selectNodeContents(input);
      var selection = window.getSelection();
      selection.removeAllRanges();
      selection.addRange(range);
    }
  }, []);

  let mainElement;

  if (showDisplay)
    mainElement = (
      <div
        id="display"
        onClick={() => {
          // the display element is replaced by an input element when user clicks on the display element
          setShowDisplay(false);
        }}
      >
        <Units text={text} showColor={showColor}></Units>
      </div>
    );
  else {
    mainElement = (
      <div
        id="input"
        contentEditable="plaintext-only"
        onBlur={(event) => {
          // the input element is replaced by a display element when user clicks outside of the input element
          setText(event.target.innerText);
          setShowDisplay(true);
        }}
      >
        {text}
      </div>
    );
  }

  return (
    <>
      <div id="menu">
        <div className="checkbox-wrapper-2">
          <input
            type="checkbox"
            className="sc-gJwTLC ikxBAC"
            name="color"
            checked={showColor}
            onChange={() => setShowColor(!showColor)}
          ></input>
        <label htmlFor="color">Color</label>
        </div>
      </div>
      <div id="main">{mainElement}</div>
    </>
  );
}

export default App;
