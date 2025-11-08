/**
 * Analytics tracking utility.
 * 
 * Tracks user events for analytics and monitoring.
 * Following Analytics role guidelines.
 */

interface AnalyticsEvent {
  event: string;
  properties?: Record<string, any>;
  timestamp?: string;
}

class Analytics {
  private enabled: boolean = true;
  
  /**
   * Track an event.
   * 
   * @param event Event name (e.g., 'interviewer_step1_complete')
   * @param properties Event properties
   */
  track(event: string, properties?: Record<string, any>) {
    if (!this.enabled) return;
    
    const analyticsEvent: AnalyticsEvent = {
      event,
      properties: {
        ...properties,
        language: localStorage.getItem('language') || 'en',
        timestamp: new Date().toISOString(),
        url: window.location.pathname,
        referrer: document.referrer
      }
    };
    
    // Log to console in development
    if (import.meta.env.DEV) {
      console.log('[Analytics]', analyticsEvent);
    }
    
    // TODO: Send to analytics service (Google Analytics, Mixpanel, etc.)
    // Example:
    // if (window.gtag) {
    //   window.gtag('event', event, properties);
    // }
    
    // Store locally for now (could be sent to backend)
    this._storeLocally(analyticsEvent);
  }
  
  /**
   * Track page view.
   * 
   * @param path Page path
   */
  pageView(path: string) {
    this.track('page_view', { path });
  }
  
  /**
   * Track flow completion.
   * 
   * @param flow 'interviewer' or 'candidate'
   * @param step Step number
   */
  flowStep(flow: string, step: number) {
    this.track(`${flow}_step${step}_complete`, { flow, step });
  }
  
  /**
   * Track analysis completion.
   * 
   * @param flow 'interviewer' or 'candidate'
   * @param analysisId Analysis ID
   */
  analysisComplete(flow: string, analysisId: string) {
    this.track('analysis_complete', { flow, analysis_id: analysisId });
  }
  
  /**
   * Track error.
   * 
   * @param error Error message
   * @param context Context where error occurred
   */
  trackError(error: string, context: string) {
    this.track('error', { error, context });
  }
  
  /**
   * Store event locally (for debugging and future sync).
   */
  private _storeLocally(event: AnalyticsEvent) {
    try {
      const events = JSON.parse(localStorage.getItem('analytics_events') || '[]');
      events.push(event);
      
      // Keep only last 100 events
      if (events.length > 100) {
        events.shift();
      }
      
      localStorage.setItem('analytics_events', JSON.stringify(events));
    } catch (e) {
      console.error('Failed to store analytics event:', e);
    }
  }
  
  /**
   * Get stored events (for debugging or batch sending).
   */
  getStoredEvents(): AnalyticsEvent[] {
    try {
      return JSON.parse(localStorage.getItem('analytics_events') || '[]');
    } catch {
      return [];
    }
  }
  
  /**
   * Clear stored events.
   */
  clearStoredEvents() {
    localStorage.removeItem('analytics_events');
  }
}

// Global analytics instance
const analytics = new Analytics();

export default analytics;

