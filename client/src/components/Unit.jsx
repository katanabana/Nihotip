import Tooltip from "./Tooltip.jsx";
import { forwardRef, useRef } from "react";

async function importAssociations() {
  const associations = {};
  const filenames = require
    .context("../assets/associations", true, /\.png/)
    .keys();
  for (const filename of filenames) {
    const character = filename.split(".")[1].slice(1);
    associations[character] = (
      await import(`../assets/associations/${filename.slice(2)}`)
    ).default;
  }
  return associations;
}

const associations = await importAssociations();

const UnitText = forwardRef(
  ({ onClick, onMouseLeave, onMouseEnter, token, color }, ref) => {
    if (!token[color] && token.subtokens) {
      const text = [];
      for (const subtoken of token.subtokens)
        text.push(
          <UnitText token={subtoken} color={color} key={text.length} />
        );
      return (
        <span
          className="unit-text"
          onMouseEnter={onMouseEnter}
          ref={ref}
          onMouseLeave={onMouseLeave}
          onClick={onClick}
        >
          {text}
        </span>
      );
    }
    return (
      <span
        onMouseEnter={onMouseEnter}
        onMouseLeave={onMouseLeave}
        onClick={onClick}
        ref={ref}
        className={"unit-text" + (token[color] ? " " + token[color] : "")}
      >
        {token.text}
      </span>
    );
  }
);

UnitText.displayName = "UnitText"; // Set display name explicitly

function Unit({ token, color, zIndex }) {
  const unitTextRef = useRef(null);

  if (typeof token === "string") return <span>{token}</span>;

  const tooltip = [];

  if (
    ["katakana", "hiragana"].includes(token["writing system"]) &&
    !token.initial
  )
    tooltip.push(
      <img key="img" src={associations[token.text]} alt={token.text} />
    );

  for (let [label, feature] of Object.entries(token)) {
    if (label === "text") continue;
    if (label === "initial") {
      tooltip.push(
        <div key={label}>
          <Unit token={feature} zIndex={zIndex + 1} />→{token.text}
        </div>
      );
      continue;
    } else if (Array.isArray(feature)) {
      const entries = Object.entries(feature);
      feature = [];
      for (const [i, subtoken] of entries) {
        feature.push(<Unit key={i} token={subtoken} zIndex={zIndex + 1} />);
        if (label !== "reading")
          feature.push(<span key={i + entries.length}>+</span>);
      }
      if (label !== "reading") feature.pop();
    } else if (typeof feature !== "string") {
      feature = <Unit token={feature} zIndex={zIndex + 1} />;
    }
    tooltip.push(
      <div key={label} className={label + " " + feature}>
        {feature}
      </div>
    );
  }

  const unitText = <UnitText token={token} color={color} ref={unitTextRef} />;

  return (
    <>
      {tooltip.length > 0 ? (
        <Tooltip
          targetRef={unitTextRef}
          target={unitText}
          content={tooltip}
          zIndex={zIndex}
        ></Tooltip>
      ) : (
        <></>
      )}
    </>
  );
}
export { Unit };
