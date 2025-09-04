function getLabelsForLanguage(lang) {
    const labels = {
        fr: {
            itineraryCalculated: "Itinéraire calculé (API réelle)",
            departure: "Départ",
            arrival: "Arrivée",
            estimatedDuration: "Durée estimée",
            distance: "Distance",
            bakeriesOnRoute: "Boulangeries sur le trajet",
            searchingBakeries: "Recherche en cours...",
            publicTransport: "Transport en commun",
            wait: "d'attente",
            metroLine1: "Métro ligne 1",
            minWait: "min d'attente",
            showRoute: "Voir l'itinéraire"
        },
        en: {
            itineraryCalculated: "Route calculated (Real API)",
            departure: "Departure",
            arrival: "Arrival",
            estimatedDuration: "Estimated duration",
            distance: "Distance",
            bakeriesOnRoute: "Bakeries on route",
            searchingBakeries: "Searching...",
            publicTransport: "Public transport",
            wait: "wait",
            metroLine1: "Metro line 1",
            minWait: "min wait",
            showRoute: "Show route"
        },
        ja: {
            itineraryCalculated: "ルート計算済み（リアルAPI）",
            departure: "出発",
            arrival: "到着",
            estimatedDuration: "推定所要時間",
            distance: "距離",
            bakeriesOnRoute: "ルート上のパン屋",
            searchingBakeries: "検索中...",
            publicTransport: "公共交通機関",
            wait: "待ち時間",
            metroLine1: "メトロ1号線",
            minWait: "分待ち",
            showRoute: "ルートを表示"
        }
    };
    return labels[lang] || labels.fr;
}
