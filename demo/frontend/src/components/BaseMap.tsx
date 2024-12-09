/* global window */
import * as React from 'react';

import {useState, useEffect} from 'react';
import {Map, Source, Layer} from 'react-map-gl';
import type {LayerProps} from 'react-map-gl';
import type {GeoJSONPoint} from '@/types/mapTypes';


// import ControlPanel from './ControlPanel';

const MAPBOX_TOKEN = process.env.MapboxAccessToken; // eslint-disable-line

const pointLayer: LayerProps = {
  id: 'point',
  type: 'circle',
  paint: {
    'circle-radius': 10,
    'circle-color': '#007cbf'
  }
};


function pointOnCircle({center, angle, radius}: {center: number[], angle: number, radius: number}): GeoJSONPoint {
  return {
    type: 'Point',
    coordinates: [center[0] + Math.cos(angle) * radius, center[1] + Math.sin(angle) * radius]
  };
}

export default function BaseMap() {
  const [pointData, setPointData] = useState<GeoJSONPoint | null>(null);

  useEffect(() => {
    const animation = window.requestAnimationFrame(() =>
      setPointData(pointOnCircle({center: [-100, 0], angle: Date.now() / 1000, radius: 20}))
    );
    return () => window.cancelAnimationFrame(animation);
  });

  return (
    <>
        <h1>Animated GeoJSON</h1>
      <Map
        initialViewState={{
          latitude: 0,
          longitude: -100,
          zoom: 3,
        //   set hight and width to vh
        }}
        style={{width: '80vw', height: '80vh'}}
        mapStyle="mapbox://styles/mapbox/light-v9"
        mapboxAccessToken={MAPBOX_TOKEN}
      >
        {pointData && (
          <Source type="geojson" data={pointData}>
            <Layer {...pointLayer} />
          </Source>
        )}
      </Map>
    </>
  );
}
