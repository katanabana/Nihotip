import React, { useState, useRef } from "react";
import ReactDOM from "react-dom";

function getTooltipPosition(tooltipRef, targetRef) {
  const tooltipElement = tooltipRef.current;
  const { top, left, width, height } =
    targetRef.current.getBoundingClientRect();
  const tooltipWidth = tooltipElement.offsetWidth;
  const tooltipHeight = tooltipElement.offsetHeight;
  let tooltipLeft =
    left + width / 2 - tooltipElement.getBoundingClientRect().width / 2;
  let tooltipTop = top - tooltipHeight - 7; // Position above the element with a margin of 10px

  // Adjust if tooltip goes out of viewport
  if (tooltipLeft + tooltipWidth > window.innerWidth) {
    tooltipLeft = window.innerWidth - tooltipWidth - 10; // Margin from right edge
  }
  if (tooltipLeft < 0) {
    tooltipLeft = 10; // Margin from left edge
  }
  if (tooltipTop < 0) {
    tooltipElement.style.setProperty("--top", "-1.5em");
    tooltipElement.style.setProperty("--bottom", "100%");
    tooltipElement.style.setProperty("--scale", "-1");
    tooltipTop = top + window.scrollY + height + 10; // Position below the element
  } else {
    tooltipElement.style.setProperty("--top", "100%");
    tooltipElement.style.setProperty("--bottom", "0");
    tooltipElement.style.setProperty("--scale", "1");
  }

  return { top: tooltipTop, left: tooltipLeft };
}

const Tooltip = ({ targetRef, target, content, zIndex }) => {
  const [visible, setVisible] = useState(false);
  const [pinned, setPinned] = useState(false);
  const [hovered, setHovered] = useState(false);
  const [position, setPosition] = useState({ top: 0, left: 0 });
  const tooltipRef = useRef(null);

  const updatePosition = () => {
    if (tooltipRef.current && targetRef.current) {
      setPosition(getTooltipPosition(tooltipRef, targetRef));
    }
  };

  const showTooltip = () => {
    updatePosition();
    setVisible(true);
    targetRef.current.classList.add("highlight");
    window.addEventListener("resize", updatePosition);
  };

  const hideTooltip = () => {
    setVisible(false);
    targetRef.current.classList.remove("highlight");
    window.removeEventListener("resize", updatePosition);
  };

  // Use React.forwardRef to forward the ref to the destination component
  const clonedChild = React.cloneElement(target, {
    ref: targetRef,
    onMouseEnter: () => showTooltip(),
    onMouseLeave: () => {
      if (!pinned && !hovered) {
        hideTooltip();
      }
    },
    onClick: () => {
      setPinned(!pinned);
      if (!pinned) {
        showTooltip();
      } else {
        hideTooltip();
      }
    },
  });

  return (
    <>
      {clonedChild}
      {ReactDOM.createPortal(
        <div
          ref={tooltipRef}
          className={"tooltip background" + (visible ? " shown" : " hidden")}
          style={{
            top: position.top,
            left: position.left,
            zIndex: visible ? zIndex : -1,
          }}
          onMouseEnter={() => {
            if (visible) {
              setHovered(true);
              showTooltip();
            }
          }}
          onMouseLeave={() => {
            setHovered(false);
            if (pinned ? true : false) {
              showTooltip();
            } else {
              hideTooltip();
            }
          }}
          onClick={() => {
            setPinned(!pinned);
            if (!pinned || hovered) {
              showTooltip();
            } else {
              hideTooltip();
            }
          }}
        >
          {content}
        </div>,
        document.getElementById("tooltips")
      )}
    </>
  );
};

export default Tooltip;
