{{/* vim: set filetype=mustache: */}}
{{/*
Expand the name of the chart.
*/}}
{{- define "kscp.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "kscp.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "kscp.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "injector.fullname" -}}
{{- printf "%s-injector" (include "kscp.fullname" .) }}
{{- end }}

{{- define "controller.fullname" -}}
{{- printf "%s-controller" (include "kscp.fullname" .) }}
{{- end }}

{{- define "certificateGenerator.fullname" -}}
{{- printf "%s-certificate-generator" (include "kscp.fullname" .) }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "kscp.labels" -}}
helm.sh/chart: {{ include "kscp.chart" . }}
{{ include "kscp.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Common selector labels
*/}}
{{- define "kscp.selectorLabels" -}}
app.kubernetes.io/name: {{ include "kscp.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}


{{/*
Injector labels
*/}}
{{- define "injector.labels" -}}
{{- include "kscp.labels" . }}
component.kscp.io: injector
{{- end }}

{{/*
Controller labels
*/}}
{{- define "controller.labels" -}}
{{- include "kscp.labels" . }}
component.kscp.io: controller
{{- end }}

{{/*
Certificate generator labels
*/}}
{{- define "certificateGenerator.labels" -}}
{{- include "kscp.labels" . }}
component.kscp.io: cert-gen
{{- end }}

{{/*
Injector selector labels
*/}}
{{- define "injector.selectorLabels" -}}
{{- include "kscp.selectorLabels" . }}
component.kscp.io: injector
{{- end }}

{{/*
Controller selector labels
*/}}
{{- define "controller.selectorLabels" -}}
{{- include "kscp.selectorLabels" . }}
component.kscp.io: controller
{{- end }}

{{/*
Create the name of the injector service account to use
*/}}
{{- define "injector.serviceAccountName" -}}
{{- if .Values.injector.serviceAccount.create }}
{{- default (printf "%s-injector" (include "kscp.fullname" .)) .Values.injector.serviceAccount.name }}
{{- else }}
{{- default (printf "%s-injector" (include "kscp.fullname" .)) .Values.injector.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the controller service account to use
*/}}
{{- define "controller.serviceAccountName" -}}
{{- if .Values.controller.serviceAccount.create }}
{{- default (printf "%s-controller" (include "kscp.fullname" .)) .Values.controller.serviceAccount.name }}
{{- else }}
{{- default (printf "%s-controller" (include "kscp.fullname" .)) .Values.controller.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the cert-gen service account to use
*/}}
{{- define "certificateGenerator.serviceAccountName" -}}
{{- if .Values.certificateGenerator.serviceAccount.create }}
{{- default (printf "%s-cert-gen" (include "kscp.fullname" .)) .Values.certificateGenerator.serviceAccount.name }}
{{- else }}
{{- default (printf "%s-cert-gen" (include "kscp.fullname" .)) .Values.certificateGenerator.serviceAccount.name }}
{{- end }}
{{- end }}