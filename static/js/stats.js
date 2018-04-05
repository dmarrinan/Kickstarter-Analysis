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
            optionChangedParentCategoryStackedBar();
        });
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
            var monthsFailed = response.failed.month_name;
            var numCampaignsFailed = response.failed.num_campaigns;
            var monthsCanceled = response.canceled.month_name;
            var numCampaignsCanceled = response.canceled.num_campaigns;

            var campaignTotals = []
            for(var i=0;i<numCampaignsSuccessful.length;i++){
                total = numCampaignsSuccessful[i] + numCampaignsFailed[i] + numCampaignsCanceled[i]
                campaignTotals.push(total)
            }

            var $radioBtnMonthStarted = document.getElementById("monthStartedRadioPercentCampaigns")
            var monthStartedScalingFactor
            if ($radioBtnMonthStarted.checked){
                ySuccess = []
                yFailed = []
                yCanceled = []
                for (var i=0;i<numCampaignsSuccessful.length;i++){
                    success = numCampaignsSuccessful[i]/campaignTotals[i]*100;
                    failed = numCampaignsFailed[i]/campaignTotals[i]*100;
                    canceled = numCampaignsCanceled[i]/campaignTotals[i]*100;
                    ySuccess.push(success);
                    yFailed.push(failed);
                    yCanceled.push(canceled);
                }
            }
            else{
                ySuccess = numCampaignsSuccessful
                yFailed = numCampaignsFailed
                yCanceled = numCampaignsCanceled
            }
            var traceSuccessful = {
                x: monthsSuccessful,
                y: ySuccess,
                name: 'Successful',
                type: 'bar',
                marker:{
                    color: '#28a745'
                }
            };

            var traceFailed = {
                x: monthsFailed,
                y: yFailed,
                name: 'Failed',
                type: 'bar',
                marker:{
                    color: '#dc3545'
                }
            };

            var traceCanceled = {
                x: monthsCanceled,
                y: yCanceled,
                name: 'Canceled',
                type: 'bar',
                marker:{
                    color: '#ffc107'
                }
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
            var lengthBinsFailed = response.failed.length_bin;
            var numCampaignsFailed = response.failed.num_campaigns;
            var lengthBinsCanceled = response.canceled.length_bin;
            var numCampaignsCanceled = response.canceled.num_campaigns;

            var campaignTotals = []
            for(var i=0;i<numCampaignsSuccessful.length;i++){
                total = numCampaignsSuccessful[i] + numCampaignsFailed[i] + numCampaignsCanceled[i]
                campaignTotals.push(total)
            }

            var $radioBtnLengthCampaign = document.getElementById("lengthCampaignRadioPercentCampaigns")
            if ($radioBtnLengthCampaign.checked){
                ySuccess = []
                yFailed = []
                yCanceled = []
                for (var i=0;i<numCampaignsSuccessful.length;i++){
                    success = numCampaignsSuccessful[i]/campaignTotals[i]*100;
                    failed = numCampaignsFailed[i]/campaignTotals[i]*100;
                    canceled = numCampaignsCanceled[i]/campaignTotals[i]*100;
                    ySuccess.push(success);
                    yFailed.push(failed);
                    yCanceled.push(canceled);
                }
            }
            else{
                ySuccess = numCampaignsSuccessful
                yFailed = numCampaignsFailed
                yCanceled = numCampaignsCanceled
            }

            var traceSuccessful = {
                x: lengthBinsSuccessful,
                y: ySuccess,
                name: 'Successful',
                type: 'bar',
                marker:{
                    color: '#28a745'
                }
            };

            var traceFailed = {
                x: lengthBinsFailed,
                y: yFailed,
                name: 'Failed',
                type: 'bar',
                marker:{
                    color: '#dc3545'
                }
            };

            var traceCanceled = {
                x: lengthBinsCanceled,
                y: yCanceled,
                name: 'Canceled',
                type: 'bar',
                marker:{
                    color: '#ffc107'
                }
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

function optionChangedParentCategoryStackedBar(){
    parentCategoriesStackedBarUrl = `/parent_category_chart/All Months/All Lengths/`
    Plotly.d3.json(parentCategoriesStackedBarUrl, function (error, response) {
        var parentCategoriesSuccessful = response.successful.parent_category;
        var numCampaignsSuccessful = response.successful.num_campaigns;
        var traceSuccessful = {
            x: parentCategoriesSuccessful,
            y: numCampaignsSuccessful,
            name: 'Successful',
            type: 'bar',
            marker:{
                color: '#28a745'
            }
        };

        var parentCategoriesFailed = response.failed.parent_category;
        var numCampaignsFailed = response.failed.num_campaigns;
        var traceFailed = {
            x: parentCategoriesFailed,
            y: numCampaignsFailed,
            name: 'Failed',
            type: 'bar',
            marker:{
                color: '#dc3545'
            }
        };

        var parentCategoriesCanceled = response.canceled.parent_category;
        var numCampaignsCanceled = response.canceled.num_campaigns;
        var traceCanceled = {
            x: parentCategoriesCanceled,
            y: numCampaignsCanceled,
            name: 'Canceled',
            type: 'bar',
            marker:{
                color: '#ffc107'
            }
        };

        var data = [traceSuccessful, traceFailed, traceCanceled];

        var layout = { barmode: 'stack' };
        Plotly.newPlot('parentCategoryStackedBar', data, layout);
        parentCategoryPlot = document.getElementById("parentCategoryStackedBar")
        parentCategoryPlot.on('plotly_click', function(data){
            categoryStackedBar(data.points[0].x);
        });
    });

    var data = [];

        var layout = { barmode: 'stack' };

        Plotly.newPlot('categoryStackedBar', data, layout);
}

function categoryStackedBar(parentCategory){
    categoriesStackedBarUrl = `/category_chart/All Months/All Lengths/${parentCategory}/`
    Plotly.d3.json(categoriesStackedBarUrl, function (error, response) {
        var categoriesSuccessful = response.successful.category_name;
        var numCampaignsSuccessful = response.successful.num_campaigns;
        var traceSuccessful = {
            x: categoriesSuccessful,
            y: numCampaignsSuccessful,
            name: 'Successful',
            type: 'bar',
            marker:{
                color: '#28a745'
            }
        };

        var categoriesFailed = response.failed.category_name;
        var numCampaignsFailed = response.failed.num_campaigns;
        var traceFailed = {
            x: categoriesFailed,
            y: numCampaignsFailed,
            name: 'Failed',
            type: 'bar',
            marker:{
                color: '#dc3545'
            }
        };

        var categoriesCanceled = response.canceled.category_name;
        var numCampaignsCanceled = response.canceled.num_campaigns;
        var traceCanceled = {
            x: categoriesCanceled,
            y: numCampaignsCanceled,
            name: 'Canceled',
            type: 'bar',
            marker:{
                color: '#ffc107'
            }
        };

        var data = [traceSuccessful, traceFailed, traceCanceled];

        var layout = { barmode: 'stack' };

        Plotly.newPlot('categoryStackedBar', data, layout);
    });
}