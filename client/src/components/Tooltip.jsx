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
const Tooltip = ({ targetRef, target, content, zIndex }) => {
  const [visible, setVisible] = useState(false);
  const [pinned, setPinned] = useState(false); // State to track if tooltip is pinned (not hidden on mouse leave)
  const [hovered, setHovered] = useState(false); // State to track if mouse is currently hovering over the tooltip
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
    updatePosition();
    setVisible(true);
    targetRef.current.classList.add("highlight"); // Add highlight class to target element
    window.addEventListener("resize", updatePosition); // Update tooltip position on window resize
  };

  // Function to hide tooltip
  const hideTooltip = () => {
    setVisible(false);
    targetRef.current.classList.remove("highlight"); // Remove highlight class from target element
    window.removeEventListener("resize", updatePosition); // Remove resize event listener
  };

  // Clone the child component and attach event handlers
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

  // Render tooltip using ReactDOM portal
  return (
    <>
      {clonedChild}{" "}
      {/* Render the cloned child component (usually a button or icon) */}
      {ReactDOM.createPortal(
        <div
          ref={tooltipRef}
          className={"tooltip background" + (visible ? " shown" : " hidden")} // Show or hide tooltip based on visibility state
          style={{
            top: position.top,
            left: position.left,
            zIndex: visible ? zIndex : -1, // Set zIndex to control visibility stack order
          }}
          onMouseEnter={() => {
            if (visible) {
              setHovered(true); // Set hovered state to true when mouse enters tooltip
              showTooltip();
            }
          }}
          onMouseLeave={() => {
            setHovered(false); // Set hovered state to false when mouse leaves tooltip
            if (pinned ? true : false) {
              showTooltip();
            } else {
              hideTooltip();
            }
          }}
          onClick={() => {
            setPinned(!pinned); // Toggle pinned state on click
            if (!pinned || hovered) {
              showTooltip();
            } else {
              hideTooltip();
            }
          }}
        >
          {content} {/* Content to display inside the tooltip */}
        </div>,
        document.getElementById("tooltips") // Render the tooltip inside the 'tooltips' element in the DOM
      )}
    </>
  );
};

export default Tooltip;
