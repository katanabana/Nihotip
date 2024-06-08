export default function Menu({ color, setColor, beingEdited, loading, hidden }) {
  const options = ["none", "part of speech", "writing system"];
  const colorSelector = (
    <div className="color">
      <div className="title">color</div>
      {options.map((option) => (
        <label key={option} className="label">
          <input
            type="radio"
            name="color"
            className="radio-input"
            value={option}
            checked={color === option}
            onChange={(event) => setColor(event.target.value)}
          />
          <div className="radio-design"></div>
          <div className="label-text">{option}</div>
        </label>
      ))}
    </div>
  );

  return (
    <div
      className={
        "background menu hiddable" +
        (hidden || beingEdited || loading ? " hidden" : "")
      }
    >
      {colorSelector}
    </div>
  );
}
