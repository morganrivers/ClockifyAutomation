<template lang="pug">
div
  h2 Categorization
  p Categorize logged activity

  b-form
    b-checkbox(v-model="fitToActive") Show Uncategorized
    b-checkbox(v-model="fitToActive") Show Google Calendar
    b-checkbox(v-model="fitToActive") Show Activity Watch

  h3 hi

  div.row
    div.col-md-6
      h4 wow1
      
      table.ui.celled.table.center.aligned
        thead
          tr
            th Avatar
            th First Name
            th Last Name
            th Email
            th Phone
            th City
        tbody
          tr
            td
              huh
            td wowwee
            td wowwee
            td wowwee
            td wowwee
            td wowwee

    div.col-md-6
      h4 wow2
      
      table.ui.celled.table.center.aligned
        thead
          tr
            th Avatar
            th First Name
            th Last Name
            th Email
            th Phone
            th City
        tbody
          tr
            td
              huh
            td wowwee
            td wowwee
            td wowwee
            td wowwee
            td wowwee

  hr

</template>

<style scoped lang="scss">
.btn {
  margin-right: 0.5em;

  .fa-icon {
    margin-left: 0;
    margin-right: 0.5em;
  }
}
</style>

<script>
import _ from 'lodash';
import moment from 'moment';

import StopwatchEntry from '../components/StopwatchEntry.vue';
import 'vue-awesome/icons/play';
import 'vue-awesome/icons/trash';

export default {
  name: 'Categorization',
  components: {
    'stopwatch-entry': StopwatchEntry,
  },
  data: () => {
    return {
      loading: true,
      bucket_id: 'aw-stopwatch',
      events: [],
      label: '',
      now: moment(),
    };
  },
  computed: {
    runningTimers() {
      return _.filter(this.events, e => e.data.running);
    },
    stoppedTimers() {
      return _.filter(this.events, e => !e.data.running);
    },
    timersByDate() {
      return _.groupBy(this.stoppedTimers, e => moment(e.timestamp).format('YYYY-MM-DD'));
    },
  },
  mounted: async function () {
    // TODO: List all possible timer buckets
    //this.getBuckets();

    // Create default timer bucket
    await this.$aw.ensureBucket(this.bucket_id, 'general.stopwatch', 'unknown');

    // TODO: Get all timer events
    await this.getEvents();

    setInterval(() => (this.now = moment()), 1000);
  },
  methods: {
    startTimer: async function (label) {
      const event = {
        timestamp: new Date(),
        data: {
          running: true,
          label: label,
        },
      };
      await this.$aw.heartbeat(this.bucket_id, 1, event);
      await this.getEvents();
    },

    updateTimer: async function (new_event) {
      const i = this.events.findIndex(e => e.id == new_event.id);
      if (i != -1) {
        // This is needed instead of this.events[i] because insides of arrays
        // are not reactive in Vue
        this.$set(this.events, i, new_event);
      } else {
        console.error(':(');
      }
    },

    removeTimer: function (event) {
      this.events = _.filter(this.events, e => e.id != event.id);
    },

    getEvents: async function () {
      this.events = await this.$aw.getEvents(this.bucket_id, { limit: 100 });
      this.loading = false;
    },
  },
};
</script>
