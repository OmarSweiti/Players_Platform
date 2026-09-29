# Test catalog

Every test the plan names, with the microstep that owns it, the repository it lives in, and the owning
step's status. The table is **generated** from the phase files by `just plan`; the plan check fails when
it is stale, when a name is claimed by two steps, or when a `done` step's test is missing or skipped at
the pinned commit.

## Conventions

- **Names** are lower_snake, at least three words, unique across the plan, and describe behaviour:
  `rls_missing_context_denies_reads_and_writes`, not `test_rls_1`.
- **Titles** contain the name verbatim — `it('rls_missing_context_denies_reads_and_writes', …)` — so the
  checker can find it. Describe blocks may group by feature; the name stays exact.
- **Location** follows the feature, never the plan, with disjoint globs per runner: backend unit
  `src/**/*.spec.ts`, integration `test/**/*.integration-spec.ts`, API `test/**/*.e2e-spec.ts`; frontend
  unit `src/**/*.test.{ts,tsx}`, browser `tests/**/*.spec.ts`. Several microsteps may extend the same file.
- **Skipped, focused or "todo" tests never count**; an empty suite fails.

## Shared fixtures

| Fixture | Holds | Used by |
|---|---|---|
| two tenants | `sadara` and `northwind`, colliding names across them, one member per role in each, a revoked session, an archived member | every authorization, isolation and data test |
| the field classification | every response field with its class — `PUBLIC`, `IDENTITY`, `MEDICAL`, `LEGAL_INTERNAL`, `FINANCE`, `MINOR` — kept independently of the code's markers | `0.6.4` and every later response |
| the test issuer | an in-process OIDC issuer that mints valid, expired, foreign-issuer, foreign-audience and replayed tokens | `0.5.4`–`0.5.8` |
| hostile files | an executable renamed `.pdf`, the EICAR string, a size-mismatched upload, a replayed presigned URL | `0.8.3`–`0.8.5` |
| canaries | a unique secret and a unique email planted in queries, bodies, headers, cookies, errors and job payloads | `0.1.4`, `0.10.2` |

All fixture data is synthetic, on `.test` domains; no real person, club or organisation appears.

## The catalog

<!-- plan:catalog:begin -->
| Test | Microstep | Repo | Status |
|---|---|---|---|
| `a_missing_progress_row_is_refused` | 0.1.3 | umbrella | done |
| `a_done_step_without_a_merged_pr_is_refused` | 0.1.3 | umbrella | done |
| `a_two_repository_step_needs_a_pr_per_repository` | 0.1.3 | umbrella | done |
| `an_unmerged_pr_is_refused` | 0.1.3 | umbrella | done |
| `a_pr_outside_the_pinned_history_is_refused` | 0.1.3 | umbrella | done |
| `a_done_step_with_an_undone_dependency_is_refused` | 0.1.3 | umbrella | done |
| `a_done_step_whose_named_test_is_missing_is_refused` | 0.1.3 | umbrella | done |
| `a_name_only_in_a_comment_is_refused` | 0.1.3 | umbrella | done |
| `a_skipped_named_test_is_refused` | 0.1.3 | umbrella | done |
| `a_skipped_suite_is_refused` | 0.1.3 | umbrella | done |
| `an_unowned_requirement_is_refused` | 0.1.3 | umbrella | done |
| `an_edited_frozen_requirement_is_refused` | 0.1.3 | umbrella | done |
| `a_broken_link_or_anchor_is_refused` | 0.1.3 | umbrella | done |
| `no_log_line_contains_a_token_or_password` | 0.1.4 | backend + frontend | todo |
| `urls_are_logged_without_query_strings` | 0.1.4 | backend + frontend | todo |
| `the_web_client_never_logs_a_request_body` | 0.1.4 | backend + frontend | todo |
| `boot_fails_without_a_required_secret` | 0.1.5 | backend | todo |
| `boot_errors_name_the_variable_but_not_its_value` | 0.1.5 | backend | todo |
| `swagger_is_served_only_in_development` | 0.1.5 | backend | todo |
| `no_local_credential_route_remains` | 0.1.6 | backend | todo |
| `protected_routes_refuse_without_a_session` | 0.1.6 | backend | todo |
| `credential_columns_are_gone` | 0.1.6 | backend | todo |
| `no_route_renders_a_password_field` | 0.1.7 | frontend | todo |
| `no_page_generates_security_codes` | 0.1.7 | frontend | todo |
| `medical_routes_are_not_found_when_disabled` | 0.1.8 | backend | todo |
| `scouting_routes_are_not_found_when_disabled` | 0.1.8 | backend | todo |
| `a_disabled_module_never_reaches_its_repository` | 0.1.8 | backend | todo |
| `harness_boots_against_an_isolated_schema` | 0.2.3 | backend | todo |
| `two_harness_runs_never_share_a_schema` | 0.2.3 | backend | todo |
| `the_unit_runner_renders_a_component` | 0.2.4 | frontend | todo |
| `each_locale_project_opens_the_sign_in_page` | 0.2.4 | frontend | todo |
| `the_built_image_answers_liveness` | 0.2.6 | backend | todo |
| `the_app_boots_on_nestjs_12` | 0.2.9 | backend | todo |
| `the_test_runner_loads_es_module_packages` | 0.2.9 | backend | todo |
| `validation_errors_list_their_fields` | 0.3.1 | backend | todo |
| `unknown_errors_leak_nothing` | 0.3.1 | backend | todo |
| `every_error_carries_the_request_id` | 0.3.1 | backend | todo |
| `a_missing_record_is_a_404_not_a_500` | 0.3.1 | backend | todo |
| `an_unknown_property_is_refused` | 0.3.2 | backend | todo |
| `a_malformed_uuid_is_a_validation_error` | 0.3.2 | backend | todo |
| `an_unknown_query_parameter_is_refused` | 0.3.2 | backend | todo |
| `routes_are_served_under_v1` | 0.3.3 | backend + frontend | todo |
| `a_single_resource_is_wrapped_once` | 0.3.4 | backend | todo |
| `a_not_found_is_never_a_200` | 0.3.4 | backend | todo |
| `timestamps_are_iso_utc` | 0.3.4 | backend | todo |
| `a_limit_above_100_is_refused` | 0.3.5 | backend | todo |
| `cursors_stay_stable_under_inserts` | 0.3.5 | backend | todo |
| `a_cursor_from_another_query_is_refused` | 0.3.5 | backend | todo |
| `an_unlisted_filter_is_refused` | 0.3.5 | backend | todo |
| `a_stale_if_match_is_refused_with_412` | 0.3.6 | backend | todo |
| `a_missing_if_match_is_refused_with_428` | 0.3.6 | backend | todo |
| `two_concurrent_edits_produce_one_winner` | 0.3.6 | backend | todo |
| `readiness_fails_when_the_database_is_down` | 0.3.7 | backend | todo |
| `readiness_fails_when_valkey_is_down` | 0.3.7 | backend | todo |
| `each_category_applies_its_own_limit` | 0.3.8 | backend | todo |
| `limits_hold_across_two_api_instances` | 0.3.8 | backend | todo |
| `a_spoofed_forwarded_for_header_is_ignored` | 0.3.8 | backend | todo |
| `the_committed_contract_matches_the_code` | 0.3.9 | backend | todo |
| `problem_details_are_declared_for_every_operation` | 0.3.9 | backend | todo |
| `preflight_reports_cross_tenant_edges` | 0.4.1 | backend | todo |
| `preflight_reports_same_parent_violations` | 0.4.1 | backend | todo |
| `preflight_output_contains_no_personal_data` | 0.4.1 | backend | todo |
| `the_runtime_role_owns_no_table` | 0.4.2 | backend + umbrella | todo |
| `the_runtime_role_cannot_run_ddl` | 0.4.2 | backend + umbrella | todo |
| `the_runtime_role_cannot_bypass_rls` | 0.4.2 | backend + umbrella | todo |
| `queries_run_inside_the_tenant_transaction` | 0.4.3 | backend | todo |
| `a_context_cannot_be_built_from_request_input` | 0.4.3 | backend | todo |
| `the_setting_does_not_outlive_its_transaction` | 0.4.3 | backend | todo |
| `foreign_keys_refuse_cross_tenant_edges` | 0.4.4 | backend | todo |
| `a_treatment_cannot_cite_another_players_record` | 0.4.4 | backend | todo |
| `attendance_cannot_mix_training_programs` | 0.4.4 | backend | todo |
| `no_composite_foreign_key_uses_set_null` | 0.4.4 | backend | todo |
| `rls_missing_context_denies_reads_and_writes` | 0.4.5 | backend | todo |
| `rls_pool_reuse_never_leaks_the_previous_tenant` | 0.4.5 | backend | todo |
| `every_tenant_table_has_forced_rls_and_a_policy` | 0.4.5 | backend | todo |
| `tenant_ids_cannot_be_updated` | 0.4.5 | backend | todo |
| `the_tenant_directory_exposes_only_routing_columns` | 0.4.5 | backend | todo |
| `every_index_on_a_tenant_table_leads_with_tenant_id` | 0.4.6 | backend | todo |
| `jod_amounts_keep_three_decimals` | 0.4.7 | backend | todo |
| `excess_scale_is_refused_not_rounded` | 0.4.7 | backend | todo |
| `money_never_passes_through_a_javascript_number` | 0.4.7 | backend | todo |
| `every_active_iso_4217_currency_is_seeded_with_its_decimals` | 0.4.7 | backend | todo |
| `a_birth_date_is_the_same_day_in_every_timezone` | 0.4.8 | backend | todo |
| `instants_round_trip_in_utc` | 0.4.8 | backend | todo |
| `an_invalid_tenant_timezone_is_refused` | 0.4.8 | backend | todo |
| `emails_are_unique_regardless_of_case_and_spacing` | 0.4.9 | backend | todo |
| `an_archived_members_email_stays_reserved` | 0.4.9 | backend | todo |
| `reactivation_restores_the_same_membership` | 0.4.9 | backend | todo |
| `impossible_values_are_refused_by_the_database` | 0.4.10 | backend | todo |
| `a_tenant_has_at_most_one_current_season` | 0.4.10 | backend | todo |
| `legal_notes_are_internal_by_default` | 0.4.10 | backend | todo |
| `high_ingest_ids_are_time_ordered` | 0.4.11 | backend | todo |
| `medical_reads_see_only_the_context_tenant` | 0.4.12 | backend | todo |
| `scouting_writes_are_stamped_with_the_context_tenant` | 0.4.12 | backend | todo |
| `the_api_client_requires_pkce` | 0.5.1 | umbrella | todo |
| `brute_force_detection_is_enabled` | 0.5.1 | umbrella | todo |
| `mfa_maps_to_assurance_level_2` | 0.5.1 | umbrella | todo |
| `sign_in_uses_the_tenant_of_the_host` | 0.5.2 | backend | todo |
| `an_unknown_host_looks_like_no_account` | 0.5.2 | backend | todo |
| `an_inactive_tenant_cannot_sign_in` | 0.5.2 | backend | todo |
| `an_identity_links_to_at_most_one_membership_per_tenant` | 0.5.3 | backend | todo |
| `sessions_store_only_token_hashes` | 0.5.3 | backend | todo |
| `id_tokens_from_another_issuer_are_refused` | 0.5.4 | backend | todo |
| `id_tokens_for_another_audience_are_refused` | 0.5.4 | backend | todo |
| `a_mismatched_nonce_is_refused` | 0.5.4 | backend | todo |
| `rotated_signing_keys_are_accepted` | 0.5.4 | backend | todo |
| `a_member_signs_in_end_to_end` | 0.5.5 | backend | todo |
| `a_non_member_gets_no_session` | 0.5.5 | backend | todo |
| `a_replayed_or_mismatched_state_is_refused` | 0.5.5 | backend | todo |
| `a_callback_from_another_browser_is_refused` | 0.5.5 | backend | todo |
| `return_to_cannot_leave_the_origin` | 0.5.5 | backend | todo |
| `the_session_cookie_is_host_only_httponly_and_secure` | 0.5.6 | backend | todo |
| `a_write_without_the_csrf_token_is_refused` | 0.5.6 | backend | todo |
| `a_write_from_another_origin_is_refused` | 0.5.6 | backend | todo |
| `a_revoked_session_fails_on_the_next_request` | 0.5.6 | backend | todo |
| `a_deactivated_member_loses_access_on_the_next_request` | 0.5.6 | backend | todo |
| `logout_revokes_the_session_server_side` | 0.5.7 | backend | todo |
| `logout_everywhere_revokes_every_session` | 0.5.7 | backend | todo |
| `a_member_cannot_revoke_another_members_session` | 0.5.7 | backend | todo |
| `a_valid_back_channel_logout_revokes_matching_sessions` | 0.5.7 | backend | todo |
| `a_forged_or_replayed_logout_token_is_refused` | 0.5.7 | backend | todo |
| `a_privileged_member_without_mfa_gets_no_session` | 0.5.8 | backend | todo |
| `a_sensitive_action_requires_recent_authentication` | 0.5.8 | backend | todo |
| `step_up_upgrades_the_existing_session` | 0.5.8 | backend | todo |
| `provisioning_creates_a_tenant_and_an_invited_owner` | 0.5.9 | backend | todo |
| `provisioning_is_idempotent_per_slug` | 0.5.9 | backend | todo |
| `provisioning_never_accepts_a_password` | 0.5.9 | backend | todo |
| `accepting_binds_the_invited_role_to_the_signed_in_identity` | 0.5.10 | backend | todo |
| `an_invitation_works_once` | 0.5.10 | backend | todo |
| `an_expired_invitation_is_refused` | 0.5.10 | backend | todo |
| `an_admin_cannot_invite_above_their_role` | 0.5.10 | backend | todo |
| `invitation_tokens_are_stored_hashed` | 0.5.10 | backend | todo |
| `the_seed_is_idempotent` | 0.5.11 | backend + umbrella + frontend | todo |
| `seed_data_uses_only_reserved_domains` | 0.5.11 | backend + umbrella + frontend | todo |
| `every_catalog_entry_can_be_stored` | 0.6.1 | backend | todo |
| `the_database_matrix_equals_the_code_matrix` | 0.6.1 | backend | todo |
| `the_permission_sync_is_idempotent` | 0.6.1 | backend | todo |
| `a_route_without_a_permission_or_public_fails_startup` | 0.6.2 | backend | todo |
| `each_route_refuses_a_member_without_its_permission` | 0.6.2 | backend | todo |
| `a_read_denied_by_policy_is_not_found` | 0.6.3 | backend | todo |
| `policies_apply_to_direct_use_case_calls` | 0.6.3 | backend | todo |
| `confidential_fields_are_absent_for_roles_without_permission` | 0.6.4 | backend | todo |
| `every_response_field_is_classified` | 0.6.4 | backend | todo |
| `an_unclassified_new_field_fails_the_suite` | 0.6.4 | backend | todo |
| `own_record_access_requires_a_live_link` | 0.6.5 | backend | todo |
| `an_expired_guardian_link_denies_access` | 0.6.5 | backend | todo |
| `the_session_lists_effective_permissions` | 0.6.6 | backend | todo |
| `a_role_change_applies_on_the_next_request` | 0.6.6 | backend | todo |
| `super_admin_reads_no_tenant_data` | 0.6.7 | backend | todo |
| `super_admin_cannot_be_granted_by_invitation` | 0.6.7 | backend | todo |
| `a_coach_cannot_read_a_medical_record` | 0.6.8 | backend | todo |
| `a_player_reads_only_their_own_medical_record` | 0.6.8 | backend | todo |
| `the_confidentiality_filter_is_not_caller_controlled` | 0.6.8 | backend | todo |
| `treatment_sessions_are_archived_not_deleted` | 0.6.8 | backend | todo |
| `patch_cannot_change_a_scouting_report_status` | 0.6.8 | backend | todo |
| `only_the_author_edits_a_report_and_only_in_draft` | 0.6.8 | backend | todo |
| `a_scouting_report_never_carries_identity_fields` | 0.6.8 | backend | todo |
| `no_route_reads_another_tenants_object` | 0.6.9 | backend | todo |
| `no_route_mutates_another_tenants_object` | 0.6.9 | backend | todo |
| `every_route_is_in_the_isolation_inventory` | 0.6.9 | backend | todo |
| `the_runtime_role_cannot_update_audit` | 0.7.1 | backend | todo |
| `the_runtime_role_cannot_delete_audit` | 0.7.1 | backend | todo |
| `truncating_audit_is_refused` | 0.7.1 | backend | todo |
| `a_rolled_back_change_leaves_no_audit_row` | 0.7.2 | backend | todo |
| `a_failed_audit_insert_aborts_the_change` | 0.7.2 | backend | todo |
| `audit_payloads_carry_no_confidential_values` | 0.7.2 | backend | todo |
| `role_changes_record_before_and_after` | 0.7.2 | backend | todo |
| `a_refused_sign_in_is_recorded_without_a_tenant` | 0.7.3 | backend | todo |
| `security_events_are_append_only` | 0.7.3 | backend | todo |
| `reading_a_medical_record_leaves_an_access_event` | 0.7.4 | backend | todo |
| `a_failed_access_audit_withholds_the_data` | 0.7.4 | backend | todo |
| `a_rolled_back_change_enqueues_nothing` | 0.7.5 | backend | todo |
| `a_duplicate_dedup_key_is_a_no_op` | 0.7.5 | backend | todo |
| `a_consumer_commits_an_event_once` | 0.7.5 | backend | todo |
| `a_crashed_worker_redelivers_and_the_handler_stays_idempotent` | 0.7.6 | backend + umbrella | todo |
| `retries_stop_at_the_bound_and_mark_dead` | 0.7.6 | backend + umbrella | todo |
| `a_job_runs_only_in_its_own_tenant` | 0.7.6 | backend + umbrella | todo |
| `the_registry_role_reads_nothing_but_tenant_ids` | 0.7.6 | backend + umbrella | todo |
| `a_replayed_command_has_one_effect` | 0.7.7 | backend | todo |
| `a_reused_key_with_a_different_body_conflicts` | 0.7.7 | backend | todo |
| `a_concurrent_duplicate_is_refused_while_in_progress` | 0.7.7 | backend | todo |
| `a_stale_lease_is_recovered_without_a_second_effect` | 0.7.7 | backend | todo |
| `a_replay_succeeds_despite_its_stale_original_if_match` | 0.7.7 | backend | todo |
| `an_invitation_notice_is_sent_in_the_recipients_locale` | 0.7.8 | backend | todo |
| `a_redelivered_event_does_not_resend_a_recorded_email` | 0.7.8 | backend | todo |
| `object_keys_are_opaque_and_tenant_prefixed` | 0.8.1 | backend | todo |
| `the_bucket_refuses_anonymous_reads` | 0.8.1 | backend | todo |
| `a_file_object_never_stores_a_url` | 0.8.2 | backend | todo |
| `sizes_beyond_two_gibibytes_are_representable` | 0.8.2 | backend | todo |
| `an_executable_renamed_pdf_is_refused` | 0.8.3 | backend | todo |
| `an_upload_for_another_tenants_owner_is_not_found` | 0.8.3 | backend | todo |
| `a_size_mismatch_is_refused` | 0.8.3 | backend | todo |
| `a_clean_file_is_promoted_to_an_immutable_version` | 0.8.4 | backend + umbrella | todo |
| `an_infected_file_is_rejected` | 0.8.4 | backend + umbrella | todo |
| `replaying_the_upload_url_after_promotion_changes_nothing` | 0.8.4 | backend + umbrella | todo |
| `a_replay_between_scan_and_copy_cannot_promote_unscanned_bytes` | 0.8.4 | backend + umbrella | todo |
| `a_scanner_outage_never_marks_a_file_clean` | 0.8.4 | backend + umbrella | todo |
| `a_download_is_pinned_to_the_scanned_version` | 0.8.5 | backend | todo |
| `a_download_for_another_tenant_is_not_found` | 0.8.5 | backend | todo |
| `an_unscanned_file_cannot_be_downloaded` | 0.8.5 | backend | todo |
| `every_internal_link_resolves` | 0.9.1 | frontend | todo |
| `an_unknown_route_renders_not_found` | 0.9.1 | frontend | todo |
| `the_catalogs_have_identical_keys` | 0.9.2 | frontend | todo |
| `the_arabic_layout_renders_rtl_on_the_server` | 0.9.2 | frontend | todo |
| `no_user_facing_literal_remains` | 0.9.2 | frontend | todo |
| `the_lint_refuses_a_physical_margin` | 0.9.3 | frontend | todo |
| `a_mixed_identifier_does_not_reorder_in_arabic` | 0.9.3 | frontend | todo |
| `a_contract_change_breaks_the_typecheck` | 0.9.4 | frontend | todo |
| `problem_details_expose_code_and_field_errors` | 0.9.4 | frontend | todo |
| `no_request_carries_a_tenant_header` | 0.9.4 | frontend | todo |
| `no_session_secret_is_readable_by_javascript` | 0.9.5 | frontend | todo |
| `an_expired_session_returns_to_sign_in_with_the_return_path` | 0.9.5 | frontend | todo |
| `logout_clears_every_cached_query` | 0.9.5 | frontend | todo |
| `navigation_hides_what_the_member_cannot_open` | 0.9.6 | frontend | todo |
| `empty_states_name_the_next_action` | 0.9.6 | frontend | todo |
| `a_failed_request_offers_retry` | 0.9.6 | frontend | todo |
| `a_request_id_reaches_the_worker_log` | 0.10.1 | backend | todo |
| `logs_carry_route_templates_not_urls` | 0.10.1 | backend | todo |
| `telemetry_canaries_never_escape` | 0.10.2 | backend | todo |
| `a_restored_stack_passes_the_catalog_tests` | 0.10.3 | umbrella + backend | todo |
| `restored_files_match_their_recorded_hashes` | 0.10.3 | umbrella + backend | todo |
| `restore_refuses_a_non_local_target` | 0.10.3 | umbrella + backend | todo |
| `the_api_recovers_when_the_database_returns` | 0.10.4 | backend | todo |
| `uploads_fail_safely_when_storage_is_down` | 0.10.4 | backend | todo |
| `auth_rate_limits_fail_closed_without_valkey` | 0.10.4 | backend | todo |
| `user_administration_preserves_last_owner_under_race` | 1.1.1 | backend | todo |
| `membership_deactivation_revokes_access_immediately` | 1.1.1 | backend | todo |
| `role_change_is_audited_and_cannot_escalate` | 1.1.1 | backend | todo |
| `tenant_settings_preserve_existing_money_and_instants` | 1.1.2 | backend + frontend | todo |
| `tenant_settings_branding_rejects_foreign_file` | 1.1.2 | backend + frontend | todo |
| `own_profile_update_cannot_change_roles_or_identity` | 1.1.3 | backend + frontend | todo |
| `profile_security_actions_use_localized_provider_flow` | 1.1.3 | backend + frontend | todo |
| `tenant_flag_cannot_override_unreleased_module` | 1.1.4 | backend | todo |
| `flag_change_is_audited_and_immediately_effective` | 1.1.4 | backend | todo |
| `permission_matrix_is_scoped_to_authorized_administrator` | 1.1.5 | backend + frontend | todo |
| `permission_matrix_distinguishes_role_from_object_policy` | 1.1.5 | backend + frontend | todo |
| `administrator_invites_and_deactivates_in_both_locales` | 1.1.6 | frontend | todo |
| `administrator_conflicting_role_edit_requires_reload` | 1.1.6 | frontend | todo |
| `test_keycloak_theme_has_required_locale_keys` | 1.1.7 | umbrella + frontend | todo |
| `keycloak_login_recovery_and_mfa_are_bilingual` | 1.1.7 | umbrella + frontend | todo |
| `membership_avatar_rejects_cross_tenant_or_pending_file` | 1.1.8 | backend + frontend | todo |
| `profile_avatar_uses_authorized_versioned_download` | 1.1.8 | backend + frontend | todo |
| `player_write_preserves_tenant_and_protected_fields` | 1.2.1 | backend | todo |
| `player_archive_is_recoverable_without_evidence_loss` | 1.2.1 | backend | todo |
| `club_history_rejects_overlapping_permanent_affiliations` | 1.2.2 | backend | todo |
| `club_upgrade_preserves_unmatched_legacy_names` | 1.2.2 | backend | todo |
| `guardian_link_revocation_denies_next_request` | 1.2.3 | backend + frontend | todo |
| `player_and_guardian_views_omit_ungranted_sections` | 1.2.3 | backend + frontend | todo |
| `player_search_preserves_names_and_scopes_results` | 1.2.4 | backend + frontend | todo |
| `player_directory_filters_are_keyboard_accessible` | 1.2.4 | backend + frontend | todo |
| `profile_completeness_uses_versioned_stage_rules` | 1.2.5 | backend + frontend | todo |
| `profile_completeness_hides_ungranted_field_details` | 1.2.5 | backend + frontend | todo |
| `duplicate_suggestions_never_reveal_hidden_players` | 1.2.6 | backend + frontend | todo |
| `player_creation_requires_duplicate_review_when_suggested` | 1.2.6 | backend + frontend | todo |
| `player_360_composes_only_permitted_module_summaries` | 1.2.7 | frontend | todo |
| `player_360_is_usable_in_mobile_rtl_and_ltr` | 1.2.7 | frontend | todo |
| `player_form_preserves_safe_input_after_validation_error` | 1.2.8 | frontend | todo |
| `player_archive_and_conflict_actions_require_confirmation` | 1.2.8 | frontend | todo |
| `typed_document_binding_requires_same_tenant_parent` | 1.3.1 | backend | todo |
| `document_upgrade_quarantines_unmapped_legacy_url` | 1.3.1 | backend | todo |
| `document_replacement_preserves_historical_file_version` | 1.3.1 | backend | todo |
| `scan_retry_cannot_promote_infected_or_changed_object` | 1.3.2 | backend + frontend | todo |
| `document_scan_failure_has_safe_accessible_retry` | 1.3.2 | backend + frontend | todo |
| `player_featured_image_is_unique_under_concurrent_changes` | 1.3.3 | backend + frontend | todo |
| `image_variant_processing_removes_location_metadata` | 1.3.3 | backend + frontend | todo |
| `player_gallery_only_displays_authorized_clean_images` | 1.3.3 | backend + frontend | todo |
| `document_retention_default_never_purges_business_evidence` | 1.3.4 | backend | todo |
| `document_cleanup_preserves_held_or_referenced_versions` | 1.3.4 | backend | todo |
| `document_upload_journey_waits_for_clean_scan` | 1.3.5 | frontend | todo |
| `document_replacement_keeps_visible_version_history` | 1.3.5 | frontend | todo |
| `contract_terms_enforce_dates_currency_and_counterparty` | 1.4.1 | backend | todo |
| `contract_current_version_belongs_to_same_contract` | 1.4.1 | backend | todo |
| `contract_state_machine_rejects_every_illegal_edge` | 1.4.2 | backend | todo |
| `contract_signing_requires_enabled_policy_and_current_evidence` | 1.4.2 | backend | todo |
| `contract_version_creation_serializes_concurrent_writers` | 1.4.3 | backend | todo |
| `contract_new_version_preserves_previous_snapshot` | 1.4.3 | backend | todo |
| `contract_access_requires_successful_redacted_audit` | 1.4.3 | backend | todo |
| `contract_retry_replays_success_despite_stale_original_revision` | 1.4.3 | backend | todo |
| `contract_expiry_uses_tenant_civil_date` | 1.4.4 | backend | todo |
| `contract_reminders_dedupe_without_driving_business_state` | 1.4.4 | backend | todo |
| `manual_signature_stays_disabled_without_approved_policy` | 1.4.5 | backend | todo |
| `signature_evidence_is_bound_to_approved_version` | 1.4.5 | backend | todo |
| `signature_evidence_cannot_be_mutated_by_runtime_role` | 1.4.5 | backend | todo |
| `contract_termination_preserves_evidence_and_cancels_reminders` | 1.4.6 | backend + frontend | todo |
| `contract_termination_requires_reason_and_confirmation` | 1.4.6 | backend + frontend | todo |
| `contract_workspace_hides_ungranted_compensation` | 1.4.7 | frontend | todo |
| `contract_workspace_respects_policy_and_civil_deadlines` | 1.4.7 | frontend | todo |
| `contract_version_file_upgrade_preserves_original_evidence` | 1.4.8 | backend | todo |
| `contract_version_sql_guards_reject_runtime_mutations` | 1.4.8 | backend | todo |
| `approval_new_version_invalidates_prior_pending_round` | 1.4.9 | backend | todo |
| `approval_decision_enforces_order_and_separation_of_duties` | 1.4.9 | backend | todo |
| `approval_race_records_one_current_version_decision` | 1.4.9 | backend | todo |
| `approval_audit_failure_rolls_back_business_change` | 1.4.9 | backend | todo |
| `contract_approval_ui_refuses_superseded_version` | 1.4.10 | frontend | todo |
| `contract_version_history_preserves_change_notes` | 1.4.10 | frontend | todo |
| `legal_ticket_state_machine_refuses_invalid_edges` | 1.5.1 | backend | todo |
| `legal_ticket_assignee_must_be_active_same_tenant_legal_user` | 1.5.1 | backend | todo |
| `legal_sla_preserves_applied_policy_and_due_instant` | 1.5.2 | backend | todo |
| `legal_overdue_retry_never_reopens_closed_ticket` | 1.5.2 | backend | todo |
| `legal_internal_notes_are_absent_from_requester_counts` | 1.5.3 | backend | todo |
| `legal_attachment_inherits_current_note_policy` | 1.5.3 | backend | todo |
| `legal_requester_finishes_case_without_internal_note_leak` | 1.5.4 | frontend | todo |
| `legal_queue_handles_conflict_and_overdue_in_both_locales` | 1.5.4 | frontend | todo |
| `legal_concurrent_assignment_returns_revision_conflict` | 1.5.5 | backend | todo |
| `legal_audit_failure_rolls_back_ticket_mutation` | 1.5.5 | backend | todo |
| `notification_rendering_is_localized_and_confidentiality_safe` | 1.6.1 | backend | todo |
| `notification_redelivery_preserves_one_in_app_record` | 1.6.1 | backend | todo |
| `notification_mark_read_is_recipient_scoped_and_idempotent` | 1.6.2 | backend + frontend | todo |
| `notification_deep_link_rechecks_current_authorization` | 1.6.2 | backend + frontend | todo |
| `mandatory_security_notification_ignores_optional_opt_out` | 1.6.3 | backend | todo |
| `mail_provider_uncertain_acceptance_is_recorded_honestly` | 1.6.3 | backend | todo |
| `notification_preferences_explain_mandatory_security_delivery` | 1.6.4 | frontend | todo |
| `audit_search_requires_explicit_permission_and_tenant_scope` | 1.7.1 | backend | todo |
| `audit_search_never_exposes_confidential_before_after` | 1.7.1 | backend | todo |
| `player_timeline_omits_unauthorized_events_and_counts` | 1.7.2 | backend | todo |
| `player_timeline_queries_modules_through_application_ports` | 1.7.2 | backend | todo |
| `audit_workspace_is_read_only_and_accessible` | 1.7.3 | frontend | todo |
| `global_search_excludes_forbidden_hits_and_counts` | 1.8.1 | backend | todo |
| `global_search_permission_change_invalidates_cached_projection` | 1.8.1 | backend | todo |
| `home_dashboard_derives_tasks_from_authorized_workflows` | 1.8.2 | backend + frontend | todo |
| `home_dashboard_handles_partial_failure_without_false_counts` | 1.8.2 | backend + frontend | todo |
| `executive_aggregate_matches_authorized_source_records` | 1.8.3 | backend + frontend | todo |
| `executive_summary_discloses_window_and_denominator` | 1.8.3 | backend + frontend | todo |
| `global_search_clears_stale_tenant_results` | 1.8.4 | frontend | todo |
| `global_search_supports_arabic_keyboard_navigation` | 1.8.4 | frontend | todo |
| `export_job_rechecks_permission_before_download` | 1.9.1 | backend | todo |
| `export_csv_neutralizes_formulas_and_excludes_confidential_fields` | 1.9.1 | backend | todo |
| `export_retry_has_one_audited_output_reference` | 1.9.1 | backend | todo |
| `export_workspace_handles_expiry_revocation_and_retry` | 1.9.2 | frontend | todo |
| `test_hosting_preflight_rejects_unapproved_residency_or_operator` | 1.10.1 | umbrella | todo |
| `test_image_build_manifest_matches_pinned_app_commits` | 1.10.2 | umbrella + backend + frontend | todo |
| `api_image_starts_with_nonowner_runtime_role` | 1.10.2 | umbrella + backend + frontend | todo |
| `web_image_serves_localized_same_origin_routes` | 1.10.2 | umbrella + backend + frontend | todo |
| `test_secret_rotation_refuses_missing_recovery_reference` | 1.10.3 | umbrella + backend | todo |
| `production_config_never_persists_provider_tokens` | 1.10.3 | umbrella + backend | todo |
| `telemetry_redacts_canaries_and_preserves_job_trace` | 1.10.4 | backend + frontend + umbrella | todo |
| `browser_telemetry_omits_sensitive_route_values` | 1.10.4 | backend + frontend + umbrella | todo |
| `test_telemetry_smoke_rejects_missing_worker_span` | 1.10.4 | backend + frontend + umbrella | todo |
| `test_backup_verification_refuses_missing_object_or_identity_backup` | 1.10.5 | umbrella | todo |
| `load_envelope_fixtures_are_tenant_isolated_and_repeatable` | 1.10.6 | backend + umbrella | todo |
| `test_load_report_rejects_failed_or_stale_thresholds` | 1.10.6 | backend + umbrella | todo |
| `test_security_gate_rejects_stale_or_high_severity_findings` | 1.10.7 | umbrella + backend | todo |
| `security_regression_covers_every_mvp_route_and_file_path` | 1.10.7 | umbrella + backend | todo |
| `mvp_pages_pass_keyboard_axe_and_responsive_checks` | 1.10.8 | frontend + umbrella | todo |
| `test_accessibility_evidence_requires_manual_screen_reader_review` | 1.10.8 | frontend + umbrella | todo |
| `mvp_acceptance_enforces_negative_business_paths` | 1.10.9 | umbrella + backend + frontend | todo |
| `mvp_staff_journeys_complete_in_both_locales` | 1.10.9 | umbrella + backend + frontend | todo |
| `test_release_evidence_rejects_unapproved_or_mismatched_pins` | 1.10.9 | umbrella + backend + frontend | todo |
| `module_boundary_gate_rejects_repository_and_framework_leaks` | 1.10.10 | backend + frontend | todo |
| `browser_boundary_gate_rejects_server_only_imports` | 1.10.10 | backend + frontend | todo |
| `test_deployment_refuses_unreviewed_pins_and_unsafe_migration` | 1.10.11 | umbrella | todo |
| `test_alert_drill_requires_delivery_and_human_acknowledgment` | 1.10.12 | umbrella | todo |
| `restored_mvp_preserves_tenant_audit_and_file_integrity` | 1.10.13 | umbrella + backend | todo |
| `test_restore_drill_refuses_production_or_missing_key_reference` | 1.10.13 | umbrella + backend | todo |
| `test_security_review_rejects_unreviewed_controls_or_high_findings` | 1.10.14 | umbrella | todo |
| `locale_switch_preserves_mvp_business_data` | 1.10.15 | umbrella + frontend | todo |
| `test_language_review_requires_provider_and_business_states` | 1.10.15 | umbrella + frontend | todo |
| `medical_activation_requires_approved_policy` | 2.1.0 | umbrella + backend | todo |
| `medical_types_preserve_unknown_legacy_values` | 2.1.1 | backend | todo |
| `medical_record_types_reject_incompatible_fields` | 2.1.1 | backend | todo |
| `medical_unassigned_user_and_unapproved_purpose_are_denied` | 2.1.2 | backend | todo |
| `medical_amendments_preserve_prior_clinical_evidence` | 2.1.2 | backend | todo |
| `medical_ciphertext_tamper_and_key_restore_are_checked` | 2.1.2 | backend | todo |
| `treatment_transition_and_responsible_clinician_are_checked` | 2.1.3 | backend | todo |
| `treatment_cannot_attach_another_players_record` | 2.1.3 | backend | todo |
| `return_to_play_requires_human_authority` | 2.1.4 | backend | todo |
| `recovery_date_never_implies_medical_clearance` | 2.1.4 | backend | todo |
| `availability_projection_omits_all_clinical_canaries` | 2.1.5 | backend | todo |
| `medical_new_tables_force_rls_and_preserve_evidence` | 2.1.6 | backend | todo |
| `medical_workspace_handles_rtl_and_revoked_access` | 2.1.7 | frontend | todo |
| `medical_canary_is_absent_from_every_unauthorized_channel` | 2.1.8 | backend + umbrella | todo |
| `medical_flag_requires_policy_and_abuse_gate` | 2.1.8 | backend + umbrella | todo |
| `training_program_validates_dates_capacity_and_money` | 2.2.1 | backend | todo |
| `training_recurrence_preserves_completed_sessions` | 2.2.2 | backend | todo |
| `training_dst_exception_has_one_occurrence` | 2.2.2 | backend | todo |
| `training_last_seat_has_one_winner` | 2.2.3 | backend | todo |
| `training_reenrollment_reactivates_existing_membership` | 2.2.3 | backend | todo |
| `training_payment_status_is_not_settlement_evidence` | 2.2.4 | backend | todo |
| `training_calendar_and_enrollment_work_in_both_locales` | 2.2.5 | frontend | todo |
| `attendance_rejects_wrong_training_and_duplicate_pair` | 2.3.1 | backend + frontend | todo |
| `attendance_correction_requires_revision_and_reason` | 2.3.1 | backend + frontend | todo |
| `completion_uses_captured_rule_and_attendance_snapshot` | 2.3.2 | backend | todo |
| `certificate_retry_preserves_one_issuance` | 2.3.3 | backend | todo |
| `certificate_arabic_render_preserves_template_provenance` | 2.3.3 | backend | todo |
| `certificate_public_verification_omits_private_details` | 2.3.4 | backend + frontend | todo |
| `revoked_certificate_displays_revoked_state` | 2.3.4 | backend + frontend | todo |
| `performance_records_reject_impossible_metric_combinations` | 2.4.1 | backend | todo |
| `performance_trends_reconcile_to_visible_source_records` | 2.4.2 | backend + frontend | todo |
| `performance_import_retry_preserves_accepted_rows` | 2.4.3 | backend | todo |
| `performance_import_reports_exact_partial_failures` | 2.4.3 | backend | todo |
| `performance_match_mapping_preserves_unknown_opponents` | 2.4.4 | backend | todo |
| `performance_import_ui_preserves_mapping_and_safe_retry` | 2.4.5 | frontend | todo |
| `rating_total_is_computed_from_immutable_scheme` | 2.5.1 | backend | todo |
| `rating_scheme_change_preserves_previous_scores` | 2.5.1 | backend | todo |
| `rating_history_exposes_scheme_changes_accessibly` | 2.5.2 | frontend | todo |
| `position_rating_scheme_captures_evaluated_position` | 2.5.3 | backend | todo |
| `chat_gateway_denies_revoked_sessions_and_foreign_rooms` | 2.6.1 | backend + umbrella | todo |
| `chat_direct_pair_and_membership_are_unique` | 2.6.2 | backend | todo |
| `conversation_images_require_current_membership` | 2.6.2 | backend | todo |
| `chat_duplicate_send_has_one_committed_sequence` | 2.6.3 | backend | todo |
| `chat_edit_and_recall_preserve_required_evidence` | 2.6.3 | backend | todo |
| `chat_read_cursor_never_moves_backwards` | 2.6.4 | backend | todo |
| `chat_reconnect_recovers_committed_messages_once` | 2.6.4 | backend | todo |
| `chat_files_cannot_launder_confidential_objects` | 2.6.5 | backend | todo |
| `chat_message_rate_and_payload_limits_hold` | 2.6.5 | backend | todo |
| `chat_ui_reconnect_preserves_one_message_and_rtl_order` | 2.6.6 | frontend | todo |
| `push_device_rotation_and_revocation_stop_delivery` | 2.7.1 | backend | todo |
| `push_payload_contains_no_confidential_canaries` | 2.7.1 | backend | todo |
| `notification_reconnect_and_deep_link_authorization_hold` | 2.7.2 | frontend | todo |
| `video_multipart_retry_and_abort_preserve_quota` | 2.8.1 | backend | todo |
| `video_old_upload_url_cannot_replace_clean_bytes` | 2.8.1 | backend | todo |
| `video_worker_variants_bind_exact_scanned_source` | 2.8.2 | backend | todo |
| `video_decoder_limits_fail_without_releasing_original` | 2.8.2 | backend | todo |
| `video_ui_never_confuses_upload_with_ready_state` | 2.8.3 | frontend | todo |
| `bulk_job_retry_and_revocation_preserve_authorized_outcomes` | 2.9.1 | backend | todo |
| `department_reports_exclude_hidden_rows_and_clinical_counts` | 2.9.2 | backend | todo |
| `operational_report_ui_handles_revoked_export_and_empty_state` | 2.9.3 | frontend | todo |
| `operations_capacity_keeps_pool_and_tenant_budgets` | 2.10.1 | backend + umbrella | todo |
| `operations_restore_preserves_messages_certificates_and_audit` | 2.10.2 | backend + umbrella | todo |
| `operations_release_manifest_requires_all_domain_gates` | 2.10.3 | umbrella + backend + frontend | todo |
| `operations_bilingual_accessibility_journeys_pass` | 2.10.4 | frontend + umbrella | todo |
| `scouting_prospect_requires_only_stage_fields` | 3.1.1 | backend | todo |
| `scouting_scores_reject_invalid_ranges` | 3.1.1 | backend | todo |
| `scouting_assignment_checks_scout_eligibility` | 3.1.2 | backend | todo |
| `scouting_reassignment_revokes_previous_access` | 3.1.2 | backend | todo |
| `scouting_review_cannot_mutate_submitted_snapshot` | 3.1.3 | backend | todo |
| `scouting_invalid_transition_and_unrelated_reviewer_are_denied` | 3.1.3 | backend | todo |
| `scouting_watchlist_is_private_by_default` | 3.1.4 | backend | todo |
| `scouting_onboarding_reuses_existing_player` | 3.1.5 | backend | todo |
| `scouting_approval_does_not_imply_enrollment_consent` | 3.1.5 | backend | todo |
| `scouting_workspace_preserves_review_history_in_both_locales` | 3.1.6 | frontend | todo |
| `scouting_activation_requires_policy_and_abuse_evidence` | 3.1.7 | backend + umbrella | todo |
| `scouting_drafts_and_protected_files_do_not_leak` | 3.1.7 | backend + umbrella | todo |
| `analytics_affiliations_preserve_historical_club_context` | 3.2.1 | backend | todo |
| `analytics_comparison_reports_sources_and_missing_data` | 3.2.2 | backend | todo |
| `analytics_cohort_excludes_unauthorized_players` | 3.2.2 | backend | todo |
| `analytics_ui_distinguishes_missing_data_from_zero` | 3.2.3 | frontend | todo |
| `dossier_snapshot_excludes_protected_field_canaries` | 3.3.1 | backend | todo |
| `dossier_archival_pdf_is_validated_before_labeling` | 3.3.1 | backend | todo |
| `sharing_grant_cannot_expand_approved_snapshot` | 3.3.2 | backend | todo |
| `sharing_revocation_denies_new_download_authority` | 3.3.2 | backend | todo |
| `sharing_portal_token_cannot_access_internal_api` | 3.3.3 | frontend + backend | todo |
| `sharing_portal_omits_capability_from_telemetry` | 3.3.3 | frontend + backend | todo |
| `dossier_approval_and_revocation_work_in_both_locales` | 3.3.4 | frontend | todo |
| `finance_ledger_balances_exact_decimal_per_currency` | 3.4.1 | backend | todo |
| `finance_posted_entries_require_reversal_not_edit` | 3.4.1 | backend | todo |
| `finance_webhook_replay_and_wrong_account_are_denied` | 3.4.2 | backend | todo |
| `finance_provider_unknown_outcome_requires_reconciliation` | 3.4.2 | backend | todo |
| `finance_training_status_derives_from_verified_allocations` | 3.4.3 | backend | todo |
| `finance_workspace_hides_compensation_from_ordinary_users` | 3.4.4 | frontend | todo |
| `finance_decimal_inputs_roundtrip_in_both_locales` | 3.4.4 | frontend | todo |
| `finance_activation_requires_approved_operating_policy` | 3.4.5 | umbrella + backend | todo |
| `finance_reconciliation_flags_amount_and_currency_mismatch` | 3.4.6 | backend | todo |
| `finance_duplicate_statement_does_not_duplicate_entries` | 3.4.6 | backend | todo |
| `signature_provider_requires_approved_evidence_policy` | 3.5.0 | umbrella + backend | todo |
| `signature_envelope_is_bound_to_approved_version` | 3.5.1 | backend | todo |
| `signature_callback_rejects_forgery_replay_and_wrong_account` | 3.5.1 | backend | todo |
| `signature_completion_requires_all_policy_evidence` | 3.5.2 | backend | todo |
| `signature_out_of_order_events_cannot_regress_contract` | 3.5.2 | backend | todo |
| `signature_restored_evidence_preserves_source_binding` | 3.5.2 | backend | todo |
| `report_schedule_rechecks_revoked_recipient_access` | 3.6.1 | backend | todo |
| `report_schedule_retry_preserves_one_local_occurrence` | 3.6.1 | backend | todo |
| `report_schedule_ui_distinguishes_acceptance_from_completion` | 3.6.2 | frontend | todo |
| `phase_three_public_and_provider_boundaries_resist_abuse` | 3.7.1 | backend + umbrella | todo |
| `phase_three_acceptance_requires_complete_evidence` | 3.7.2 | umbrella | todo |
| `phase_three_capacity_envelope_meets_agreed_budgets` | 3.7.3 | backend + umbrella | todo |
| `phase_three_restore_preserves_finance_and_signature_evidence` | 3.7.4 | backend + umbrella | todo |
| `platform_operator_has_no_implicit_business_data_access` | 4.1.1 | backend | todo |
| `platform_session_requires_no_hidden_tenant_membership` | 4.1.1 | backend | todo |
| `support_grant_requires_distinct_approver_and_current_assurance` | 4.1.2 | backend | todo |
| `support_expiry_immediately_denies_subsequent_actions` | 4.1.2 | backend | todo |
| `platform_provisioning_retry_creates_one_tenant` | 4.1.3 | backend | todo |
| `platform_provisioning_failure_is_resumable_without_hidden_access` | 4.1.3 | backend | todo |
| `custom_role_cannot_exceed_assigner_or_policy_ceiling` | 4.1.4 | backend | todo |
| `custom_role_revocation_applies_on_next_request` | 4.1.4 | backend | todo |
| `tenant_usage_reconciliation_preserves_exact_counts` | 4.1.5 | backend | todo |
| `tenant_entitlement_does_not_grant_data_permission` | 4.1.5 | backend | todo |
| `tenant_suspension_revokes_sessions_jobs_and_realtime` | 4.1.6 | backend | todo |
| `tenant_offboarding_preserves_held_evidence` | 4.1.6 | backend | todo |
| `tenant_noisy_neighbor_cannot_starve_other_tenant` | 4.1.7 | backend | todo |
| `tenant_quota_reservation_recovers_after_worker_crash` | 4.1.7 | backend | todo |
| `platform_workspace_shows_real_actor_and_support_scope` | 4.1.8 | frontend | todo |
| `enterprise_sso_never_links_identity_by_email` | 4.2.1 | backend + umbrella | todo |
| `identity_provider_exit_preserves_membership_and_revocation` | 4.2.1 | backend + umbrella | todo |
| `passkey_recovery_cannot_bypass_privileged_assurance` | 4.2.2 | backend + frontend | todo |
| `passkey_provider_screens_support_both_locales` | 4.2.2 | backend + frontend | todo |
| `rls_inventory_rejects_unprotected_new_tenant_table` | 4.3.1 | backend | todo |
| `legal_hold_blocks_all_linked_retention_actions` | 4.3.2 | backend | todo |
| `legal_hold_release_requires_authorized_approval` | 4.3.2 | backend | todo |
| `scale_candidate_preserves_authorization_and_capacity` | 4.3.3 | backend + umbrella | todo |
| `platform_upgrade_restores_sql_objects_and_identity_config` | 4.3.4 | backend + umbrella | todo |
| `outbound_webhook_blocks_private_network_and_redirect_targets` | 4.4.1 | backend | todo |
| `outbound_webhook_retry_reuses_stable_event_identity` | 4.4.1 | backend | todo |
| `partner_credential_cannot_exceed_tenant_object_scope` | 4.4.2 | backend | todo |
| `partner_credential_revocation_applies_on_next_request` | 4.4.2 | backend | todo |
| `calendar_consent_excludes_confidential_event_content` | 4.4.3 | backend | todo |
| `calendar_disconnect_stops_jobs_and_revokes_connector` | 4.4.3 | backend | todo |
| `integration_admin_exposes_scope_without_stored_secrets` | 4.4.4 | frontend | todo |
| `assistance_activation_requires_approved_data_policy` | 4.5.1 | umbrella + backend | todo |
| `assistance_summary_requires_human_acceptance_and_current_sources` | 4.5.2 | backend + frontend | todo |
| `assistance_output_cannot_execute_business_commands` | 4.5.2 | backend + frontend | todo |
| `assistance_review_ui_requires_explicit_human_acceptance` | 4.5.2 | backend + frontend | todo |
| `assistance_evaluation_blocks_injection_and_cross_tenant_canaries` | 4.5.3 | backend + umbrella | todo |
| `assistance_unapproved_model_version_is_disabled` | 4.5.3 | backend + umbrella | todo |
| `native_session_profile_cannot_bypass_app_revocation` | 4.6.1 | backend + umbrella | todo |
| `mobile_readiness_recovers_without_persistent_confidential_cache` | 4.6.2 | frontend | todo |
| `phase_four_acceptance_requires_second_agency_evidence` | 4.7.1 | umbrella | todo |
| `phase_four_workload_preserves_two_tenant_isolation` | 4.7.2 | backend + umbrella | todo |
| `phase_four_capacity_resists_skewed_tenant_load` | 4.7.2 | backend + umbrella | todo |
<!-- plan:catalog:end -->
