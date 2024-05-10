import { useState } from "react";

async function importAssociations() {
  /* require.context() and import() throw errors if the directory is passed through a variable */
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

function UnitText({ token, color }) {
  if (!token[color] && token.subtokens) {
    const text = [];
    /* perform recursion on the subtokens in hopes of the feature presenting in them */
    for (const subtoken of token.subtokens)
      text.push(
        <UnitText token={subtoken} color={color} key={text.length}></UnitText>
      );
    return <span className="unit-text">{text}</span>;
  }
  /* feature that should be marked with color is present in the token or the token can't be subdivided further */
  return (
    <span className={"unit-text" + (token[color] ? " " + token[color] : "")}>
      {token.text}
    </span>
  );
}

function Unit({ token, color }) {
  color;
  const [showTooltip, setShowTooltip] = useState(false);

  if (typeof token === "string") return <span>{token}</span>;

  const tooltip = [];

  if (["katakana", "hiragana"].includes(token["writing system"]))
    tooltip.push(<img key="img" src={associations[token.text]}></img>);

  for (let [label, feature] of Object.entries(token)) {
    if (label === "text") continue;
    if (label === "initial") {
      tooltip.push(
        <div key={label}>
          <Unit token={feature}></Unit>→{token.text}
        </div>
      );
      continue;
    } else if (Array.isArray(feature)) {
      // feature is an array of tokens
      const entries = Object.entries(feature);
      feature = [];
      for (const [i, subtoken] of entries) {
        feature.push(<Unit key={i} token={subtoken}></Unit>);
        if (label != "reading")
          feature.push(<span key={i + entries.length}>+</span>);
      }
      if (label != "reading") feature.pop();
    } else if (typeof feature != "string") {
      // feature is a token
      feature = <Unit token={feature}></Unit>;
    }
    tooltip.push(<div key={label}>{feature}</div>);
  }
  return (
    <span
      className={
        "unit tooltip-container" + (showTooltip ? " show-tooltip" : "")
      }
      onClick={() => setShowTooltip(!showTooltip)}
    >
      <UnitText token={token} color={color} start={0}></UnitText>

      {tooltip.length > 0 && (
        <span className="tooltip background">{tooltip}</span>
      )}
    </span>
  );
}
export { Unit };
