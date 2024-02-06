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
  // Tokenizing api doesn't reflect where spaces and lines breaks are in text.
  // There for this information should be memorized before tokenizing text.
  // Text elements gotten after applying split are considered independent and processed by api as completely separate strings.

  const textItems = {};
  const lines = text.split("\n");
  let index = 0;
  for (let i = 0; i < lines.length; i++) {
    lines[i] = lines[i].split(" ");
    for (let j = 0; j < lines[i].length; j++) {
      lines[i][j] = lines[i][j].split("　");
      for (const itemText of lines[i][j]) {
        textItems[index] = itemText;
        index++;
      }
    }
  }

  const linesDivs = [];
  const linesTexts = text.split("\n");
  for (let i = 0; i < linesTexts.length; i++) {
    linesDivs.push(<div key={i}>{linesTexts[i]}</div>);
  }
  const [units, setUnits] = useState(linesDivs);
  // send request to api to get text tokens:
  useEffect(() => {
    const params = new URLSearchParams(textItems);
    const url = process.env.REACT_APP_API_URL + "/tokenize?" + params;
    fetch(url, { mode: "cors" })
      .then((respnose) => respnose.json())
      .then((keysToTokens) => {
        // create collections of html elements representing parts of text:
        const newUnits = [];
        index = 0;
        for (let i = 0; i < lines.length; i++) {
          for (let j = 0; j < lines[i].length; j++) {
            for (let h = 0; h < lines[i][j].length; h++) {
              const tokens = keysToTokens[index.toString()];
              for (
                let token_index = 0;
                token_index < tokens.length;
                token_index++
              ) {
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
                    <span key={`big-unit-${index}-${token_index}`}>
                      {token.text}
                    </span>
                  );
                }
              }
              index++;
              if (h != lines[i][j].length - 1)
                newUnits.push(
                  <span
                    key={`japanese-space-${i}-${j}-${h}`}
                    style={{ whiteSpace: "pre" }}
                  >
                    {"　"}
                  </span>
                );
            }
            if (j != lines[i].length - 1)
              newUnits.push(
                <span
                  key={`plain-space-${i}-${j}`}
                  style={{ whiteSpace: "pre" }}
                >
                  {" "}
                </span>
              );
          }
          if (i != lines.length - 1)
            newUnits.push(<br key={`line-break-${i}`}></br>);
        }
        setUnits(newUnits);
      });
  }, [text, showColor]);
  return units;
}
