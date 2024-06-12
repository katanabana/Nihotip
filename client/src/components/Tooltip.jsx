import React, { useState, useRef } from 'react';
import ReactDOM from 'react-dom';
import './Tooltip.css'; // Ensure to add CSS for tooltip styling

const Tooltip = ({ children, content }) => {
  const [visible, setVisible] = useState(false);
  const [position, setPosition] = useState({ top: 0, left: 0 });
  const tooltipRef = useRef(null);

  const showTooltip = (event) => {
    const tooltipElement = tooltipRef.current;
    if (!tooltipElement) return;

    const { top, left, width, height } = event.target.getBoundingClientRect();
    const tooltipWidth = tooltipElement.offsetWidth;
    const tooltipHeight = tooltipElement.offsetHeight;

    let tooltipLeft = left + window.scrollX;
    let tooltipTop = top + window.scrollY - tooltipHeight - 10; // Position above the element with a margin of 10px

    // Adjust if tooltip goes out of viewport
    if (tooltipLeft + tooltipWidth > window.innerWidth) {
      tooltipLeft = window.innerWidth - tooltipWidth - 10; // Margin from right edge
    }
    if (tooltipLeft < 0) {
      tooltipLeft = 10; // Margin from left edge
    }
    if (tooltipTop < 0) {
      tooltipTop = top + window.scrollY + height + 10; // Position below the element
    }

    setPosition({ top: tooltipTop, left: tooltipLeft });
    setVisible(true);
  };

  const hideTooltip = () => {
    setVisible(false);
  };

  return (
    <>
      {React.cloneElement(children, {
        onMouseEnter: showTooltip,
        onMouseLeave: hideTooltip,
      })}
      {visible &&
        ReactDOM.createPortal(
          <div
            ref={tooltipRef}
            className="tooltip"
            style={{ top: position.top, left: position.left }}
          >
            {content}
          </div>,
          document.body
        )}
    </>
  );
};

export default Tooltip;