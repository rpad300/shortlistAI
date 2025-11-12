import { useEffect } from 'react';
import { trackEvent } from '@utils/analytics';

interface AdminAnalyticsProps {
  page: string;
  data?: Record<string, any>;
}

export const useAdminAnalytics = ({ page, data }: AdminAnalyticsProps) => {
  useEffect(() => {
    // Track admin page views
    trackEvent('admin_page_view', {
      page,
      admin_session: true,
      timestamp: new Date().toISOString(),
      ...data
    });
  }, [page, data]);

  // Helper function to track admin actions
  const trackAdminAction = (actionType: string, additionalData?: Record<string, any>) => {
    trackEvent('admin_action', {
      page,
      action: actionType,
      admin_session: true,
      timestamp: new Date().toISOString(),
      ...data,
      ...additionalData
    });
  };

  return { trackAdminAction };
};

// Specific hooks for common admin actions
export const useAdminPageAnalytics = (pageName: string) => {
  return useAdminAnalytics({ page: pageName });
};

export const useAdminDashboardAnalytics = () => {
  const { trackAdminAction } = useAdminAnalytics({ page: 'admin_dashboard' });

  const trackDashboardAction = (action: string, data?: Record<string, any>) => {
    trackAdminAction(`dashboard_${action}`, data);
  };

  return { trackDashboardAction };
};

export const useAdminCandidatesAnalytics = () => {
  const { trackAdminAction } = useAdminAnalytics({ page: 'admin_candidates' });

  const trackCandidatesAction = (action: string, data?: Record<string, any>) => {
    trackAdminAction(`candidates_${action}`, data);
  };

  return { trackCandidatesAction };
};

export const useAdminAnalysesAnalytics = () => {
  const { trackAdminAction } = useAdminAnalytics({ page: 'admin_analyses' });

  const trackAnalysesAction = (action: string, data?: Record<string, any>) => {
    trackAdminAction(`analyses_${action}`, data);
  };

  return { trackAnalysesAction };
};
