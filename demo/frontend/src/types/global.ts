export interface GeoJSONPoint {
  type: 'Point';
  coordinates: number[];
}

export type Vehicle = {
  vehicle_id: string;
  confidence: number;
  color: string;
};