import { useEffect, useState } from "react";
import process from "process";
//import {isDigraph, specialKana, basicCharacter} from "./dictionary.jsx"

const url = process.env.REACT_APP_API_URL + "\\tags_to_colors";
const tagsToColors = await fetch(url).then((response) => response.json());

function Components({ elements, func = (x) => x }) {
  const components = [];
  let key = 0;
  for (const element of elements) {
    components.push(<span key={key}>{func(element)}</span>);
    key++;
  }
  return <div>{components}</div>;
}

function Unit({ text, tooltipItems, showColor, tag }) {
  const tooltip = [];
  for (let i = 0; i < tooltipItems.length; i++) {
    tooltip.push(<div key={i}>{tooltipItems[i]}</div>);
  }
  const style = {};
  if (tag)
    tooltip.push(
      <div style={style} key={tooltipItems.length}>
        {tag}
      </div>
    );
  if (tagsToColors[tag] && showColor) {
    style.color = tagsToColors[tag];
  } else {
    style.color = "#d1d0c5";
  }
  return (
    <span className="unit">
      <span className="unit-text" style={style}>
        {text}
      </span>
      {tooltip.length > 0 && <span className="tooltip">{tooltip}</span>}
    </span>
  );
}

function SmallUnit({ text, showColor, tag }) {
  return (
    <Unit text={text} tooltipItems={[]} showColor={showColor} tag={tag}></Unit>
  );
}

function MediumUnit({ subtoken, showColor }) {
  const hiragana = (
    <Components
      elements={subtoken.hiragana}
      func={(character) => (
        <SmallUnit
          text={character}
          showColor={showColor}
          tag={"hiragana"}
        ></SmallUnit>
      )}
    ></Components>
  );
  return (
    <Unit
      text={subtoken.text}
      tooltipItems={[hiragana]}
      showColor={showColor}
      tag={subtoken.tag}
    ></Unit>
  );
}

function BigUnit({ token, showColor }) {
  const subtokens = Object.values(token.subtokens);
  const sum = (
    <Components
      elements={subtokens}
      func={(subtoken) => (
        <span>
          <MediumUnit subtoken={subtoken} showColor={showColor}></MediumUnit>
          {subtoken != subtokens[subtokens.length - 1] && <span>+</span>}
        </span>
      )}
    ></Components>
  );

  return (
    <Unit
      text={token["text"]}
      showColor={showColor}
      tooltipItems={[sum]}
      tag={token["tag"]}
    ></Unit>
  );
}

export default function Units({ text, showColor }) {
  const [units, setUnits] = useState(linesDivs);
  // send request to api to get text tokens:
  useEffect(() => {
    const url = process.env.REACT_APP_API_URL + "/tokenize?text=" + text;
    fetch(url, { mode: "cors" })
      .then((respnose) => respnose.json())
      .then((tokens) => {
        const newUnits = [];
        for (let token_index = 0; token_index < tokens.length; token_index++) {
          const tokenMap = new Map(Object.entries(tokens[token_index]));
          const token = {};
          for (const [key, value] of tokenMap) {
            token[key] = value;
          }
          if (Object.keys(token).length > 1) {
            newUnits.push(
              <BigUnit
                key={`big-unit-${index}-${token_index}`}
                token={token}
                showColor={showColor}
              ></BigUnit>
            );
          } else {
            newUnits.push(
              <span key={`big-unit-${index}-${token_index}`}>{token.text}</span>
            );
          }
        }
        setUnits(newUnits);
      });
  }, [text, showColor]);
  return units;
}
