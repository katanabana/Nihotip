import { useState, useEffect } from "react";
import process from "process"; // Node.js process module imported (typically for environment variables)
import { Unit } from "./components/Unit.jsx"; // Importing custom components
import Menu from "./components/Menu.jsx";
import { addText, History } from "./components/History.jsx";
import useKeyboardStatus from './components/useKeyboardStatus.jsx'; // Import the custom hook
import editIcon from "./assets/icons/edit.png"; // Importing icons
import displayIcon from "./assets/icons/display.png";
import loaderIcon from "./assets/icons/loader.png";
import settingsIcon from "./assets/icons/settings.png";

// Asynchronous function to fetch tokens from API
async function getTokens(text) {
  let url = process.env.REACT_APP_API_URL; // Using environment variable for API URL
  url += "/tokens?text=";
  url += text.replaceAll("\n", "%0A"); // Replace newline characters with URL encoding
  const response = await fetch(url, { mode: "cors" }); // Fetching data from API
  return await response.json(); // Parsing response as JSON
}

function App() {
  // State variables using hooks
  const [text, setText] = useState(""); // Text input state
  const [tokens, setTokens] = useState([]); // Tokens state
  const [beingEdited, setBeingEdited] = useState(true); // Editing mode state
  const [color, setColor] = useState("part of speech"); // Color state for display
  const [currentText, setCurrentText] = useState(false); // Current text state
  const [loading, setLoading] = useState(false); // Loading state
  const [hidden, setHidden] = useState(true); // Hidden state for settings menu
  const isKeyboardOpen = useKeyboardStatus();

  const maxText = 2000; // Maximum length of text allowed

  // Effect hook to handle fetching tokens when text changes and not being edited
  useEffect(() => {
    if (beingEdited) return; // Skip if still being edited
    setLoading(true); // Set loading state true
    getTokens(text).then((tokens) => {
      setTokens(tokens); // Update tokens state with fetched data
      setLoading(false); // Set loading state false
      addText(text); // Add text to history
    });
  }, [text]); // Dependency on text changes

  // JSX for text component based on editing mode
  const textComponent = beingEdited ? (
    <div
      className="input"
      contentEditable="plaintext-only"
      suppressContentEditableWarning={true}
      onInput={(event) => setCurrentText(event.target.innerText)}
      // Text area for input (not to be confused with "text" state)
    >
      {text}
    </div>
  ) : (
    <div className="display">
      {/* Display tokens as Unit components */}
      {Array.from(tokens.entries(), ([i, token]) => {
        return <Unit key={i} token={token} color={color} zIndex={1000} unitId={[i]}></Unit>;
      })}
    </div>
  );

  // Function to toggle editing mode
  function changeMode() {
    if (beingEdited && currentText !== text) {
      setText(currentText); // Update text state with current text
      setTokens([currentText]); // Update tokens state
    }
    if (!beingEdited) setLoading(false); // Set loading to false if not being edited
    setBeingEdited(!beingEdited); // Toggle editing mode
    setText(currentText); // Update text state with current text
  }

  // JSX for mode button (edit/display)
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
        src={beingEdited ? displayIcon : editIcon} // Display icon based on editing mode
        onClick={changeMode} // Click handler to change mode
      ></img>
    </div>
  );

  // JSX for word count display
  const wordCount = (
    <div
      className={
        "word-count hiddable" +
        (currentText.length >= 0.75 * maxText && beingEdited ? "" : " hidden") +
        (currentText.length > maxText ? " overflow" : "")
      }
    >
      {`${currentText.length} / ${maxText}`} {/* Display current text length */}
    </div>
  );

  // Main JSX return for App component
  return (
    <div className={`app-container ${isKeyboardOpen ? 'keyboard-open' : ''}`}>
      <div id="tooltips"></div>
      <Menu
        color={color}
        setColor={setColor}
        loading={loading}
        beingEdited={beingEdited}
        hidden={hidden}
      ></Menu>
      <div className="text-container">
        {wordCount} {/* Display word count */}
        <div className={"background text" + (loading ? " blur" : "")}>
          {textComponent} {/* Display text component */}
          <img
            className={"loader hiddable" + (loading ? "" : " hidden")}
            src={loaderIcon} // Loader icon
          ></img>
        </div>
        <nav>
          <img
            className={
              "settings button hiddable" +
              (beingEdited || loading ? " hidden" : "")
            }
            onClick={() => setHidden(!hidden)} // Click handler to toggle settings visibility
            src={settingsIcon} // Settings icon
          ></img>
          {mode} {/* Display mode button */}
        </nav>
      </div>
      <History
        // History component for displaying and selecting text from history
        setText={(text) => {
          document.getElementsByClassName("input")[0].innerHTML = text;
          setCurrentText(text);
        }}
        hidden={currentText || history.length === 0} // History visibility
      ></History>
    </div>
  );
}

export default App;
