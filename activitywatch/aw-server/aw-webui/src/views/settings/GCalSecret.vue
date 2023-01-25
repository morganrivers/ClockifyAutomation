<template lang="pug">
div
  div.d-flex.justify-content-between
    div
      h5.mb-0 Google Calendar secret URL
    div
      b-form-input(v-model="inputText" type="text")
  small
    | Enter the secret URL for your Google Calendar.
</template>

<script>
import { useSettingsStore } from '~/stores/settings';

export default {
  computed: {
    isEnabled: {
      get() {
        const settingsStore = useSettingsStore();
        return settingsStore.gcalSecret.isEnabled;
      },
      set(value) {
        const settingsStore = useSettingsStore();
        const data = settingsStore.gcalSecret;
        settingsStore.update({
          gcalSecret: { ...data, isEnabled: value },
        });
      },
    },
  },
};
</script>
