import { mouseWheelZoom } from 'mouse-wheel-zoom';

const wz = mouseWheelZoom({
  element: document.querySelector('[data-wheel-zoom]'),
  zoomStep: .25  
});

// reset zoom
wz.reset();