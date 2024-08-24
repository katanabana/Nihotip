import Tooltip from "./Tooltip.jsx";
import { forwardRef, useRef } from "react";

const tree = {}
let tooltipId = 0


// Function to asynchronously import association images
async function importAssociations() {
  const associations = {};
  const filenames = require
    .context("../assets/associations", true, /\.png/)
    .keys();

  // Iterate over filenames and import each association image
  for (const filename of filenames) {
    const character = filename.split(".")[1].slice(1); // Extract character from filename
    associations[character] = (
      await import(`../assets/associations/${filename.slice(2)}`)
    ).default; // Dynamically import association image
  }
  return associations;
}

// Import associations and store them
const associations = await importAssociations();

// ForwardRef component for UnitText, which handles text display with event handlers
const UnitText = forwardRef(
  ({ onClick, onMouseLeave, onMouseEnter, token, color }, ref) => {
    // Recursive rendering if token has subtokens
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

    // Render unit text span with class based on color if applicable
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

// Main Unit component that renders a token with its tooltip if applicable
function Unit({ token, color, zIndex }) {
  const unitTextRef = useRef(null); // Reference for unit text span

  // If token is a string, render it directly
  if (typeof token === "string") return <span>{token}</span>;

  const tooltip = []; // Array to store tooltip content
  const currentId = tooltipId;
  const dependencies = [];

  // Conditionally add association image to tooltip based on token attributes
  if (
    ["katakana", "hiragana"].includes(token["writing system"]) &&
    !token.initial
  )
    tooltip.push(
      <img key="img" src={associations[token.text]} alt={token.text} />
    );

  // Iterate over token attributes and build tooltip content
  for (let [label, feature] of Object.entries(token)) {
    if (label === "text") continue; // Skip rendering 'text' attribute directly

    // Special handling for 'initial' and array attributes
    if (label === "initial") {
      tooltip.push(
        <div key={label}>
          <Unit token={feature} zIndex={zIndex + 1} />→{token.text}
        </div>
      );
      tooltipId += 1
      dependencies.push(tooltipId)
      continue;
    } else if (Array.isArray(feature)) {
      const entries = Object.entries(feature);
      feature = [];
      for (const [i, subtoken] of entries) {
        feature.push(<Unit key={i} token={subtoken} zIndex={zIndex + 1} />);
        tooltipId += 1
        dependencies.push(tooltipId)
        if (label !== "reading")
          feature.push(<span key={i + entries.length}>+</span>);
      }
      if (label !== "reading") feature.pop();
    } else if (typeof feature !== "string") {
      feature = <Unit token={feature} zIndex={zIndex + 1} />;
      tooltipId += 1
      dependencies.push(tooltipId)
    }

    // Push attribute and feature into tooltip content array
    tooltip.push(
      <div key={label} className={label + " " + feature}>
        {feature}
      </div>
    );
  }

  // Render UnitText component with ref for tooltip positioning
  const unitText = <UnitText token={token} color={color} ref={unitTextRef} />;
  tree[currentId] = dependencies

  // Render Tooltip component if tooltip content exists
  return (
    <>
      {tooltip.length > 0 ? (
        <Tooltip
          targetRef={unitTextRef}
          target={unitText}
          content={tooltip}
          zIndex={zIndex}
          dependencies={dependencies}
        ></Tooltip>
      ) : (
        <></>
      )}
    </>
  );
}

export { Unit };
