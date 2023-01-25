<template lang="pug">
div
  div.d-flex.justify-content-between
    div
      h5.mb-0 Use Spacy
    div
      b-form-checkbox(v-model="isEnabled" switch)
  small
    | Turn on machine learning.
</template>

<script>
import { useSettingsStore } from '~/stores/settings';

export default {
  computed: {
    isEnabled: {
      get() {
        const settingsStore = useSettingsStore();
        return settingsStore.useSpacyData.isEnabled;
      },
      set(value) {
        const settingsStore = useSettingsStore();
        const data = settingsStore.useSpacyData;
        settingsStore.update({
          useSpacyData: { ...data, isEnabled: value },
        });
      },
    },
  },
};
</script>
