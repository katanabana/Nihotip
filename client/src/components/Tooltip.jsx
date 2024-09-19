import React, { useState, useRef } from "react";
import ReactDOM from "react-dom";

// Function to calculate tooltip position relative to a target element
function getTooltipPosition(tooltipRef, targetRef) {
  const tooltipElement = tooltipRef.current;
  const { top, left, width, height } =
    targetRef.current.getBoundingClientRect();
  const tooltipWidth = tooltipElement.offsetWidth;
  const tooltipHeight = tooltipElement.offsetHeight;

  // Calculate initial tooltip position
  let tooltipLeft =
    left + width / 2 - tooltipElement.getBoundingClientRect().width / 2;
  let tooltipTop = top - tooltipHeight - 7; // Position above the element with a margin of 7px

  // Adjust tooltip position if it goes out of viewport
  if (tooltipLeft + tooltipWidth > window.innerWidth) {
    tooltipLeft = window.innerWidth - tooltipWidth - 10; // Margin from the right edge
  }
  if (tooltipLeft < 0) {
    tooltipLeft = 10; // Margin from the left edge
  }
  if (tooltipTop < 0) {
    // Position below the element if tooltip would go above viewport
    tooltipElement.style.setProperty("--top", "-1.5em");
    tooltipElement.style.setProperty("--bottom", "100%");
    tooltipElement.style.setProperty("--scale", "-1");
    tooltipTop = top + window.scrollY + height + 10; // Position below the element with a margin of 10px
  } else {
    tooltipElement.style.setProperty("--top", "100%");
    tooltipElement.style.setProperty("--bottom", "0");
    tooltipElement.style.setProperty("--scale", "1");
  }

  return { top: tooltipTop, left: tooltipLeft };
}

// Tooltip component definition
const Tooltip = ({ targetRef, target, content, zIndex, unitId }) => {
  const [visible, setVisible] = useState(false);
  const [position, setPosition] = useState({ top: 0, left: 0 }); // State for tooltip position
  const tooltipRef = useRef(null);

  // Function to update tooltip position
  const updatePosition = () => {
    if (tooltipRef.current && targetRef.current) {
      setPosition(getTooltipPosition(tooltipRef, targetRef));
    }
  };

  // Function to show tooltip
  const showTooltip = () => {
    document.getElementById(
      `tooltip-${unitId.join("-")}`
    ).style.zIndex = `${zIndex}`;
    for (const element of document.getElementsByClassName("tooltip shown")) {
      if (!`tooltip-${unitId.join("-")}`.startsWith(element.id)) {
        element.classList.remove("shown");
        element.classList.add("hidden");
        document
          .getElementById(
            "unit-text-" + element.id.split("-").slice(1).join("-")
          )
          .classList.remove("highlight");
        setTimeout(() => {
          element.style.zIndex = "-1";
        }, 500);
      }
    }
    updatePosition();
    setVisible(true);
    targetRef.current.classList.add("highlight"); // Add highlight class to target element
    window.addEventListener("resize", updatePosition); // Update tooltip position on window resize
    let tooltipId = "tooltip";
    let z = 1;
    for (const i of unitId) {
      tooltipId += `-${i}`;
      const classes = document.getElementById(tooltipId).classList;
      classes.remove("hidden");
      classes.add("shown");
      document.getElementById(tooltipId).style.zIndex = z;
      z += 1;
    }
  };

  // Function to hide tooltip
  // Function to hide tooltip
  const hideTooltip = (withAncestors) => {
    setVisible(false);
    targetRef.current.classList.remove("highlight"); // Remove highlight class from target element
    window.removeEventListener("resize", updatePosition); // Remove resize event listener
    if (withAncestors) {
      let tooltipId = "tooltip";
      for (const i of unitId) {
        // Declare a new block-scoped variable for each iteration
        let currentTooltipId = tooltipId + `-${i}`;
        const classes = document.getElementById(currentTooltipId).classList;
        setTimeout(() => {
          document.getElementById(currentTooltipId).style.zIndex = -1;
        }, 500);
        classes.remove("shown");
        classes.add("hidden");
      }
    }
  };

  // Clone the child component and attach event handlers
  const clonedChild = React.cloneElement(target, {
    ref: targetRef,
    onMouseEnter: () => {
      showTooltip();
    },
    onMouseLeave: () => {
      setTimeout(() => {
        if (
          !document
            .getElementById(`tooltip-${unitId.join("-")}`)
            .classList.contains("hovered")
        ) {
          hideTooltip(false);
        }
      }, 100);
    },
  });

  const tooltipStyle = {
    top: position.top,
    left: position.left,
  };
  if (visible) {
    tooltipStyle["zIndex"] = zIndex;
  }
  // Render tooltip using ReactDOM portal
  return (
    <>
      {clonedChild}{" "}
      {/* Render the cloned child component (usually a button or icon) */}
      {ReactDOM.createPortal(
        <div
          ref={tooltipRef}
          id={`tooltip-${unitId.join("-")}`}
          className={"tooltip background" + (visible ? " shown" : " hidden")} // Show or hide tooltip based on visibility state
          style={tooltipStyle}
          onMouseEnter={() => {
            document
              .getElementById(`tooltip-${unitId.join("-")}`)
              .classList.add("hovered");
            showTooltip();
          }}
          onMouseLeave={() => {
            document
              .getElementById(`tooltip-${unitId.join("-")}`)
              .classList.remove("hovered");
            hideTooltip(true);
          }}
          onClick={showTooltip}
        >
          {content} {/* Content to display inside the tooltip */}
        </div>,
        document.getElementById("tooltips") // Render the tooltip inside the 'tooltips' element in the DOM
      )}
    </>
  );
};

export default Tooltip;
