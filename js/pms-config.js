/**
 * PMS Configuration — New Ridge Family Dental
 * Set your practice management system details here.
 */

export const PMS_CONFIG = {
  /**
   * Mode: 'mock' | 'json' | 'opendental' | 'dentrix' | 'generic'
   *
   * - mock:    Uses built-in demo data (no external system needed)
   * - json:    Loads from local JSON files in /data/ directory
   * - opendental: Connects to Open Dental REST API
   * - dentrix: Connects via Dentrix API (requires proxy/CORS)
   * - generic: Connects to any REST API you configure
   */
  mode: 'mock',

  /**
   * Patient ID to load on page open.
   * Set to null to show a patient search/selector instead.
   */
  defaultPatientId: '78429',

  /**
   * JSON File Mode Settings
   * Place exported patient JSON files in /data/patients/
   * Place exported radiograph JSON files in /data/radiographs/
   */
  json: {
    patientsPath: './data/patients/',
    radiographsPath: './data/radiographs/',
    fileExtension: '.json'
  },

  /**
   * Open Dental REST API Settings
   * Open Dental must have the API plugin enabled.
   * Docs: https://www.opendental.com/site/api.html
   */
  openDental: {
    baseUrl: 'https://your-opendental-server.com/api',
    username: 'your-api-username',
    password: 'your-api-password',
    // Set to true if your Open Dental server sends CORS headers
    directCors: false,
    // If directCors is false, set a proxy URL (e.g. Netlify function, Vercel edge)
    proxyUrl: ''
  },

  /**
   * Dentrix API Settings
   * Dentrix requires a middleware/proxy due to CORS restrictions.
   */
  dentrix: {
    // Dentrix G/6 API endpoint or Henry Schein One integration URL
    baseUrl: 'https://api.dentrix.com/v1',
    apiKey: 'your-dentrix-api-key',
    // Proxy/middleware URL that adds auth and CORS
    proxyUrl: ''
  },

  /**
   * Generic REST API Settings
   * Use this for any custom PMS or middleware you build.
   */
  generic: {
    baseUrl: 'https://your-api-server.com',
    apiKey: '',
    headers: {},
    // Endpoint paths — override if your API uses different URLs
    endpoints: {
      patient: '/patients/{id}',
      patientRadiographs: '/patients/{id}/radiographs',
      radiograph: '/radiographs/{id}',
      analysis: '/radiographs/{id}/analysis'
    }
  },

  /**
   * Cache settings
   */
  cache: {
    enabled: true,
    ttlMinutes: 5
  }
};
