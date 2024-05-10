import { useState } from "react";
import settingsIcon from "../assets/icons/settings.png";

export default function Menu({ color, setColor, beingEdited, loading }) {
  const [hidden, setHidden] = useState(true);
  const colorSelector = (
    <label>
      {"color"}
      <select
        name="color"
        defaultValue={color}
        onChange={(event) => setColor(event.target.value)}
      >
        {["none", "part of speech", "writing system"].map((option) => (
          <option key={option} value={option} className="select-item">
            {option}
          </option>
        ))}
      </select>
    </label>
  );

  return (
    <>
      <nav className={"hiddable" + (beingEdited || loading ? " hidden" : "")}>
        <img
          className={"button"}
          onClick={() => setHidden(!hidden)}
          src={settingsIcon}
        ></img>
        <div
          className={
            "background menu hiddable" +
            (hidden || beingEdited || loading ? " hidden" : "")
          }
        >
          {colorSelector}
        </div>
      </nav>
    </>
  );
}
