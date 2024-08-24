export default function Menu({
  color,
  setColor,
  beingEdited,
  loading,
  hidden,
}) {
  // Define options for color selection
  const options = ["none", "part of speech", "writing system"];

  // Component for rendering color selector
  const colorSelector = (
    <div className="color">
      <div className="title">color</div>
      {options.map((option) => (
        <label key={option} className="label">
          {/* Radio input for each color option */}
          <input
            type="radio"
            name="color"
            className="radio-input"
            value={option}
            checked={color === option} // Check if current color matches this option
            onChange={(event) => setColor(event.target.value)} // Update color state on selection change
          />
          <div className="radio-design"></div>{" "}
          {/* Visual design for radio button */}
          <div className="label-text">{option}</div>{" "}
          {/* Display text for color option */}
        </label>
      ))}
    </div>
  );

  // Render menu component with conditional visibility based on props
  return (
    <div
      className={
        "background menu hiddable" +
        (hidden || beingEdited || loading ? " hidden" : "") // Hide menu if hidden, being edited, or loading
      }
    >
      {colorSelector} {/* Render color selector component */}
    </div>
  );
}
