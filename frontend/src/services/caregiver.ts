import { api } from './api'
import type { CaregiverLink, CaregiverAlert, CaregiverReport, SeniorProgressResponse } from '../types/models'

export function getLinkedSeniors() {
  return api<CaregiverLink[]>('/caregiver/seniors')
}

export function getSeniorProgress(seniorId: string) {
  return api<SeniorProgressResponse>(`/caregiver/senior/${seniorId}/progress`)
}

export function linkSenior(email: string) {
  return api<CaregiverLink>('/caregiver/link', {
    method: 'POST',
    body: JSON.stringify({ senior_email: email }),
  })
}

export function getCaregiverAlerts() {
  return api<CaregiverAlert[]>('/caregiver/alerts')
}

export function getCaregiverReports() {
  return api<CaregiverReport[]>('/caregiver/reports')
}
