//populate select element with possible parent category values
parentCategoriesUrl = "/fetch_parent_categories";
Plotly.d3.json(parentCategoriesUrl, function (error, response) {
    if (error) console.log(error);
    parentCategoryList = ['All Parent Categories'];
    for (var i = 0; i < response.length; i++) {
        parentCategoryList.push(response[i]);
    }

    $parentCategorySelectListMonthStarted = document.getElementById("parentCategorySelectMonthStarted");
    $parentCategorySelectListLengthCampaign = document.getElementById("parentCategorySelectLengthCampaign");
    for (var i = 0; i < parentCategoryList.length; i++) {
        var $optionMonthStarted = document.createElement("option");
        $optionMonthStarted.value = parentCategoryList[i];
        $optionMonthStarted.text = parentCategoryList[i];
        $parentCategorySelectListMonthStarted.appendChild($optionMonthStarted);

        var $optionLengthCampaign = document.createElement("option");
        $optionLengthCampaign.value = parentCategoryList[i];
        $optionLengthCampaign.text = parentCategoryList[i];
        $parentCategorySelectListLengthCampaign.appendChild($optionLengthCampaign);
    }

    //populate select element with possible category values
    //use parent category to narrow down possible selections
    parentCategoryMonthStarted = $parentCategorySelectListMonthStarted.value
    categoriesMonthStartedUrl = `/fetch_categories_month_started/${parentCategoryMonthStarted}`;
    Plotly.d3.json(categoriesMonthStartedUrl, function (error, response) {
        if (error) console.log(error);
        categoryList = ['All Categories'];
        for (var i = 0; i < response.length; i++) {
            categoryList.push(response[i]);
        }

        $categorySelectListMonthStarted = document.getElementById("categorySelectMonthStarted");
        for (var i = 0; i < categoryList.length; i++) {
            var $optionMonthStarted = document.createElement("option");
            $optionMonthStarted.value = categoryList[i];
            $optionMonthStarted.text = categoryList[i];
            $categorySelectListMonthStarted.appendChild($optionMonthStarted);
        }
        optionChangedMonthStartedStackedBar($parentCategorySelectListMonthStarted.id);
    });

    parentCategoryLengthCampaign = $parentCategorySelectListLengthCampaign.value
    categoriesLengthCampaignUrl = `/fetch_categories_length_campaign/${parentCategoryLengthCampaign}`;
    Plotly.d3.json(categoriesLengthCampaignUrl, function (error, response) {
        if (error) console.log(error);
        categoryList = ['All Categories'];
        for (var i = 0; i < response.length; i++) {
            categoryList.push(response[i]);
        }

        $categorySelectListLengthCampaign = document.getElementById("categorySelectLengthCampaign");
        for (var i = 0; i < categoryList.length; i++) {
            var $optionLengthCampaign = document.createElement("option");
            $optionLengthCampaign.value = categoryList[i];
            $optionLengthCampaign.text = categoryList[i];
            $categorySelectListLengthCampaign.appendChild($optionLengthCampaign);
        }
        optionChangedLengthCampaignStackedBar($parentCategorySelectListLengthCampaign.id);
    });
});

function optionChangedMonthStartedStackedBar(selectListId) {
    //populate select element with possible category values
    //use parent category to narrow down possible selections
    parentCategoryMonthStarted = $parentCategorySelectListMonthStarted.value

    categoriesMonthStartedUrl = `/fetch_categories_month_started/${parentCategoryMonthStarted}`;
    Plotly.d3.json(categoriesMonthStartedUrl, function (error, response) {
        if (error) console.log(error);
        categoryList = ['All Categories'];

        if (selectListId == $parentCategorySelectListMonthStarted.id) {
            //clear drop down
            removeOptions($categorySelectListMonthStarted)
        }

        for (var i = 0; i < response.length; i++) {
            categoryList.push(response[i]);
        }
        //console.log(medalList);
        $categorySelectListMonthStarted = document.getElementById("categorySelectMonthStarted");
        for (var i = 0; i < categoryList.length; i++) {
            var $optionMonthStarted = document.createElement("option");
            $optionMonthStarted.value = categoryList[i];
            $optionMonthStarted.text = categoryList[i];
            $categorySelectListMonthStarted.appendChild($optionMonthStarted);
        }

        monthStartedStackedBarUrl = `/month_started_chart/${$parentCategorySelectListMonthStarted.value}/${$categorySelectListMonthStarted.value}/`
        Plotly.d3.json(monthStartedStackedBarUrl, function (error, response) {
            var monthsSuccessful = response.successful.month_name;
            var numCampaignsSuccessful = response.successful.num_campaigns;
            var traceSuccessful = {
                x: monthsSuccessful,
                y: numCampaignsSuccessful,
                name: 'Successful',
                type: 'bar'
            };

            var monthsFailed = response.failed.month_name;
            var numCampaignsFailed = response.failed.num_campaigns;
            var traceFailed = {
                x: monthsFailed,
                y: numCampaignsFailed,
                name: 'Failed',
                type: 'bar'
            };

            var monthsCanceled = response.canceled.month_name;
            var numCampaignsCanceled = response.canceled.num_campaigns;
            var traceCanceled = {
                x: monthsCanceled,
                y: numCampaignsCanceled,
                name: 'Canceled',
                type: 'bar'
            };

            var data = [traceSuccessful, traceFailed, traceCanceled];

            var layout = { barmode: 'stack' };

            Plotly.newPlot('monthStartedStackedBar', data, layout);
        });
    });
}

function optionChangedLengthCampaignStackedBar(selectListId) {
    parentCategoryLengthCampaign = $parentCategorySelectListLengthCampaign.value
    categoriesLengthCampaignUrl = `/fetch_categories_length_campaign/${parentCategoryLengthCampaign}`;

    Plotly.d3.json(categoriesLengthCampaignUrl, function (error, response) {
        if (error) console.log(error);
        categoryList = ['All Categories'];

        if (selectListId == $parentCategorySelectListLengthCampaign.id) {
            //clear drop down
            removeOptions($categorySelectListLengthCampaign)
        }

        for (var i = 0; i < response.length; i++) {
            categoryList.push(response[i]);
        }

        $categorySelectListLengthCampaign = document.getElementById("categorySelectLengthCampaign");
        for (var i = 0; i < categoryList.length; i++) {
            var $optionLengthCampaign = document.createElement("option");
            $optionLengthCampaign.value = categoryList[i];
            $optionLengthCampaign.text = categoryList[i];
            $categorySelectListLengthCampaign.appendChild($optionLengthCampaign);
        }

        lengthCampaignStackedBarUrl = `/length_campaign_chart/${$parentCategorySelectListLengthCampaign.value}/${$categorySelectListLengthCampaign.value}/`
        Plotly.d3.json(lengthCampaignStackedBarUrl, function (error, response) {
            var lengthBinsSuccessful = response.successful.length_bin;
            var numCampaignsSuccessful = response.successful.num_campaigns;
            var traceSuccessful = {
                x: lengthBinsSuccessful,
                y: numCampaignsSuccessful,
                name: 'Successful',
                type: 'bar'
            };

            var lengthBinsFailed = response.failed.length_bin;
            var numCampaignsFailed = response.failed.num_campaigns;
            var traceFailed = {
                x: lengthBinsFailed,
                y: numCampaignsFailed,
                name: 'Failed',
                type: 'bar'
            };

            var lengthBinsCanceled = response.canceled.length_bin;
            var numCampaignsCanceled = response.canceled.num_campaigns;
            var traceCanceled = {
                x: lengthBinsCanceled,
                y: numCampaignsCanceled,
                name: 'Canceled',
                type: 'bar'
            };

            var data = [traceSuccessful, traceFailed, traceCanceled];

            var layout = { barmode: 'stack' };

            Plotly.newPlot('lengthCampaignstackedBar', data, layout);
        });
    });
}

function removeOptions(selectbox) {
    var i;
    for (i = selectbox.options.length - 1; i >= 0; i--) {
        selectbox.remove(i);
    }
}