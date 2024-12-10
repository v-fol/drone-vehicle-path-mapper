import { useState, useEffect } from "react";
import { Map, Source, Layer } from "react-map-gl";
import type { LayerProps } from "react-map-gl";
import PathJson from "@/pathGEO.json";

import { useAtom } from "jotai";
import {
  isAnimatingAtom,
  visibleDataAtom,
  currentIndexAtom,
  mapStyleAtom,
} from "@/atoms";
import { foundVehiclesImagesAtom } from "@/atoms";

import { Vehicle } from "@/types/global";

const startingPoint = {
  type: "Feature",
  geometry: {
    type: "Point",
    coordinates: [25.914562, 48.267013],
  },
  properties: {
    vehicle_id: "Drone start",
    timestamp: "2024-12-09T17:38:03Z",
    color: "#04ED86",
  },
};

PathJson.features.unshift(startingPoint);

const MAPBOX_TOKEN = ""

const pointLayer: LayerProps = {
  id: "point",
  type: "circle",

  paint: {
    "circle-radius": ["match", ["get", "vehicle_id"], "Drone start", 10, 5],
    "circle-opacity": ["match", ["get", "vehicle_id"], "Drone start", 0.5, 1],
    "circle-color": ["get", "color"],
  },
};

export default function BaseMap() {
  const [visibleData, setVisibleData] = useAtom(visibleDataAtom);
  const [currentIndex, setCurrentIndex] = useAtom(currentIndexAtom);
  const [isAnimating, setIsAnimating] = useAtom(isAnimatingAtom);
  const [foundVehiclesImages, setFoundVehiclesImages] = useAtom(
    foundVehiclesImagesAtom
  );
  const [mapStyle] = useAtom(mapStyleAtom);

  useEffect(() => {
    if (!isAnimating) return;

    const sortedFeatures = PathJson.features.sort(
      (a, b) =>
        new Date(a.properties.timestamp).getTime() -
        new Date(b.properties.timestamp).getTime()
    );

    if (currentIndex >= sortedFeatures.length) {
      setIsAnimating(false);
      return;
    }

    const animatePoints = () => {
      setVisibleData((prevData) => ({
        ...prevData,
        features: [
          ...prevData.features,
          sortedFeatures[currentIndex] as GeoJSON.Feature,
        ],
      }));

      if (foundVehiclesImages.length === 0) {
        setFoundVehiclesImages([
          {
            vehicle_id: sortedFeatures[currentIndex].properties.vehicle_id,
            confidence: 0.9,
            color: sortedFeatures[currentIndex].properties.color,
          },
        ]);
      }
      const found = foundVehiclesImages.find(
        (vehicle) =>
          vehicle.vehicle_id ===
          sortedFeatures[currentIndex].properties.vehicle_id
      );
      if (!found) {
        setFoundVehiclesImages([
          ...foundVehiclesImages,
          {
            vehicle_id: sortedFeatures[currentIndex].properties.vehicle_id,
            confidence: 0.9,
            color: sortedFeatures[currentIndex].properties.color,
          },
        ]);
      }

      if (currentIndex < sortedFeatures.length - 1) {
        const currentTimestamp = new Date(
          sortedFeatures[currentIndex].properties.timestamp
        ).getTime();
        const nextTimestamp = new Date(
          sortedFeatures[currentIndex + 1].properties.timestamp
        ).getTime();
        const delay = nextTimestamp - currentTimestamp;

        setTimeout(() => {
          setCurrentIndex((prevIndex) => prevIndex + 1);
        }, delay);
      } else {
        setIsAnimating(false);
      }
    };

    animatePoints();
  }, [isAnimating, currentIndex]);

  return (
    <>
      <div className=" overflow-hidden rounded-xl mr-2">
        <Map
          initialViewState={{
            latitude: 48.267136,
            longitude: 25.924092,
            zoom: 14,
            // pitch: 42,
            //   bearing: -50,
          }}
          style={{ width: "100vw", height: "80vh" }}
          mapStyle={mapStyle}
          mapboxAccessToken={MAPBOX_TOKEN}
          interactiveLayerIds={["point"]} // Ensures hover only works for point layers
        >
          <Source type="geojson" data={visibleData}>
            <Layer {...pointLayer} />
          </Source>
        </Map>
      </div>
    </>
  );
}
