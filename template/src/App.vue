<template>
<!-- TradingVueJs 101 (example from 'Getting Started' ) -->

<trading-vue :data="chart" :width="this.width" :height="this.height"
    :color-back="colors.colorBack"
    :color-grid="colors.colorGrid"
    :color-text="colors.colorText">
</trading-vue>
</template>

<script>
import TradingVue from 'trading-vue-js'
import Data from '../data/data.json'

export default {
    name: 'app',
    components: { TradingVue },
    methods: {
        onResize(event) {
            this.width = window.innerWidth
            this.height = window.innerHeight
        }
    },
    mounted() {
        window.addEventListener('resize', this.onResize)
    },
    beforeDestroy() {
        window.removeEventListener('resize', this.onResize)
    },
    data() {
        return {
            chart: Data,
            width: window.innerWidth,
            height: window.innerHeight,
            colors: {
                colorBack: '#121826',
                colorGrid: '#2f3240',
                colorText: '#dedddd',
                colorTextHL: '#fff',
                colorTitle: '#42b883',
                colorCross: '#8091a0'
            }
        }
    }
}
</script>
