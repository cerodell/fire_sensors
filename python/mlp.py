# %% [markdown]
# Standardize and check it out
# %%

keep_vars = ['PM1 [ug/m3]', 'UBC_PM_03_pm10_env']
df = df_final.drop(columns=[col for col in df_final if col not in keep_vars])
df['UBC_PM_03_pm10_env2'] = df['UBC_PM_03_pm10_env']

scaler = MinMaxScaler()
scaled = scaler.fit_transform(df)

# df_stnd = df_final
df.tail()
# %% [markdown]
# Break data up into:
# - Target variable: y
# - predictor variable(s): x
# %%
y = scaled[:,0]
x = scaled[:,1:]

# def unison_shuffled_copies(a, b):
#     assert len(a) == len(b)
#     p = np.random.permutation(len(a))
#     return a[p], b[p]

# x, y = unison_shuffled_copies(x,y)
  
# %% [markdown]
# Break data up into training and target variabels
fracTrain = 0.8 
ntrain = int(np.floor(fracTrain * len(x)))

# x = np.stack((x, x), axis = 1)
x_train = x[:ntrain]  
y_train = y[:ntrain]

x_test = x[ntrain:]  
y_test = y[ntrain:]


# ## define a precentage of training data
# fracTrain = 0.8 
# ntrain = int(np.floor(fracTrain * len(x)))

# # subset training  
# x_train = x[:ntrain]  
# y_train = y[:ntrain]
# # subset target
# x_test = x[ntrain:]  
# y_test = y[ntrain:]

# %%
##### Play around with these parameters
num_models = 1  # number of models to build for the ensemble
min_nhn = 1  # minimum number of hidden neurons to loop through (nhn = 'number hidden neurons')
max_nhn = 12  # maximum number of hidden neurons to loop through
max_hidden_layers = (
    2  # maximum number of hidden layers to loop through (nhl = 'number hidden layers')
)
batch_size = 32
solver = "sgd"  # use stochastic gradient descent as an optimization method (weight updating algorithm)
activation = "relu"
learning_rate_init = 0.001
max_iter = 1500  # max number of epochs to run
early_stopping = True  # True = stop early if validation error begins to rise
validation_fraction = 0.2  # fraction of training data to use as validation
#####

# %%
y_out_all_nhn = []
y_out_ensemble = []
RMSE_ensemble = []  # RMSE for each model in the ensemble
nhn_best = []
nhl_best = []

def rmse(target, prediction):
    return np.sqrt(((target - prediction) ** 2).sum() / len(target))

for model_num in range(num_models):  # for each model in the ensemble

    print("Model Number: " + str(model_num))

    RMSE = []
    y_out_all_nhn = []
    nhn = []
    nhl = []

    for num_hidden_layers in range(1, max_hidden_layers + 1):

        print("\t # Hidden Layers = " + str(num_hidden_layers))

        for num_hidden_neurons in range(
            min_nhn, max_nhn + 1
        ):  # for each number of hidden neurons

            print("\t\t # hidden neurons = " + str(num_hidden_neurons))

            hidden_layer_sizes = (num_hidden_neurons, num_hidden_layers)
            model = MLPRegressor(
                hidden_layer_sizes=hidden_layer_sizes,
                verbose=False,
                max_iter=max_iter,
                early_stopping=early_stopping,
                validation_fraction=validation_fraction,
                batch_size=batch_size,
                solver=solver,
                activation=activation,
                learning_rate_init=learning_rate_init,
            )

            model.fit(x_train, y_train)  # train the model

            y_out_this_nhn = model.predict(
                x_test
            )  # model prediction for this number of hidden neurons (nhn)
            y_out_all_nhn.append(
                y_out_this_nhn
            )  # store all models -- will select best one best on RMSE

            RMSE.append(rmse(y_test, y_out_this_nhn))  # RMSE between cumulative curves

            nhn.append(num_hidden_neurons)
            nhl.append(num_hidden_layers)

    indBest = RMSE.index(np.min(RMSE))  # index of model with lowest RMSE
    RMSE_ensemble.append(np.min(RMSE))
    nhn_best.append(nhn[indBest])
    nhl_best.append(nhl[indBest])
    # nhn_best.append(indBest+1) #the number of hidden neurons that achieved best model performance of this model iteration
    y_out_ensemble.append(y_out_all_nhn[indBest])

    print(
        "\t BEST: "
        + str(nhl_best[model_num])
        + " hidden layers, "
        + str(nhn_best[model_num])
        + " hidden neurons"
    )

y_out_ensemble_mean = np.mean(y_out_ensemble, axis=0)
RMSE_ensemble_mean = rmse(y_out_ensemble_mean, y_test)

test  = np.column_stack((y_out_ensemble_mean,x_test))
unscaled = scaler.inverse_transform(test)
y_out_ensemble_mean = unscaled[:,0]
y_test = df['PM1 [ug/m3]'].values[ntrain:]
# %%
plt.figure(figsize=(12, 8))

plt.subplot(241)
plt.scatter(len(RMSE_ensemble), RMSE_ensemble_mean, c="k", marker="*")
plt.scatter(range(len(RMSE_ensemble)), RMSE_ensemble)
plt.xlabel("Model #")
plt.ylabel("RMSE")
plt.title("Error")

plt.subplot(242)
plt.scatter(range(len(nhn_best)), nhn_best)
plt.xlabel("Model #")
plt.ylabel("# Hidden Neurons")
plt.title("Hidden Neurons")

plt.subplot(243)
plt.scatter(range(len(nhl_best)), nhl_best)
plt.xlabel("Model #")
plt.ylabel("# Hidden Layers")
plt.title("Hidden Layers")

plt.subplot(244)
plt.scatter(y_test, y_out_ensemble_mean)
# plt.plot((np.min(y_test),np.max(y_test)),'k--')
plt.xlabel("y_test")
plt.ylabel("y_model")
plt.title("Ensemble")

plt.subplot(212)
plt.plot(y_out_ensemble_mean)
plt.plot(y_test, alpha=0.5)

plt.tight_layout()



# %%
# saveIt = 0

# plt.figure(figsize=(12, 5))

# plt.scatter(range(len(y_test)), y_test, label="Observations", zorder=0, alpha=0.3)
# plt.plot(
#     range(len(y_test)),
#     np.transpose(y_out_ensemble[0]),
#     color="k",
#     alpha=0.4,
#     label="Individual Models",
#     zorder=1,
# )  # plot first ensemble member with a label
# plt.plot(
#     range(len(y_test)), np.transpose(y_out_ensemble[1:]), color="k", alpha=0.4, zorder=1
# )  # plot remaining ensemble members without labels for a nicer legend
# plt.plot(
#     range(len(y_test)),
#     y_out_ensemble_mean,
#     color="k",
#     label="Ensemble",
#     zorder=2,
#     linewidth=3,
# )
# plt.xlabel("Time", fontsize=20)
# plt.ylabel("y", fontsize=20)
# plt.xticks(fontsize=16)
# plt.yticks(fontsize=16)
# plt.title("MLP Model Results", fontsize=24)
# plt.legend(fontsize=16, loc="best")

# plt.tight_layout()
























# %%
bias_pm = {}
for num in range(1,6):
    df_final[f'UBC_PM_0{num}_pm10_cor'] =  df_final[f'UBC_PM_0{num}_pm10_env'] + (df_final[f'UBC_PM_0{num}_pm10_env'].mean() - df_final['PM1 [ug/m3]'].mean())
    df_final[f'UBC_PM_0{num}_pm25_cor'] =  df_final[f'UBC_PM_0{num}_pm25_env'] + (df_final[f'UBC_PM_0{num}_pm25_env'].mean() - df_final['PM2.5 [ug/m3]'].mean())
    df_final[f'UBC_PM_0{num}_pm100_cor'] =  df_final[f'UBC_PM_0{num}_pm100_env'] + (df_final[f'UBC_PM_0{num}_pm100_env'].mean() - df_final['PM10 [ug/m3]'].mean())





    # bias_pm.update({f'UBC_PM_0{num}_pm10_bias': df_final[f'UBC_PM_0{num}_pm10_env'].mean() - df_final['PM1 [ug/m3]'].mean()})
    # bias_pm.update({f'UBC_PM_0{num}_pm25_bias': df_final[f'UBC_PM_0{num}_pm25_env'].mean() - df_final['PM2.5 [ug/m3]'].mean()})
    # bias_pm.update({f'UBC_PM_0{num}_pm100_bias': df_final[f'UBC_PM_0{num}_pm100_env'].mean() - df_final['PM10 [ug/m3]'].mean()})


# %% [markdown]
# ### Plot Bias Corrected PM 1.0 
# %%



fig = plt.figure(figsize=(14, 12))
fig.autofmt_xdate()
xfmt = DateFormatter("%m-%d %H:00")
fig.suptitle(r"PM 1.0 ($\frac{\mu g}{m^3}$)", fontsize=16)
ax = fig.add_subplot(2, 1, 2)
ax.plot(df_final.index,df_final['PM1 [ug/m3]'], lw = 4.0, label = 'GRIMM', color = colors[0])
ax.plot(df_final.index,df_final['UBC_PM_01_pm10_cor'], label = 'UBC-PM-01', color = colors[1])
# ax.plot(df_final.index,df_final['UBC_PM_02_pm10_env'], label = 'UBC-PM-02', color = colors[2])
ax.plot(df_final.index,df_final['UBC_PM_03_pm10_cor'], label = 'UBC-PM-03', color = colors[2])
ax.plot(df_final.index,df_final['UBC_PM_04_pm10_cor'], label = 'UBC-PM-04', color = colors[3])
ax.plot(df_final.index,df_final['UBC_PM_05_pm10_cor'], label = 'UBC-PM-05', color = colors[4])
ax.set_ylabel(r'$\frac{\mu g}{m^3}$', rotation=0)
ax.set_xlabel('Time (MM-DD HH)')
ax.legend(
    loc="upper center",
    bbox_to_anchor=(0.5, 2.44),
    ncol=6,
    fancybox=True,
    shadow=True,
)
ax = fig.add_subplot(2, 2, 1)
size = 6
ax.scatter(df_final['PM1 [ug/m3]'], df_final['PM1 [ug/m3]'], s=size, color = colors[0])
ax.scatter(df_final['PM1 [ug/m3]'], df_final['UBC_PM_01_pm10_cor'], s=size, color = colors[1])
# ax.scatter(df_grim['PM1 [ug/m3]'], df_final['UBC_PM_02_pm10_env'], s=size, color = colors[2])
ax.scatter(df_final['PM1 [ug/m3]'], df_final['UBC_PM_03_pm10_cor'], s=size, color = colors[2])
ax.scatter(df_final['PM1 [ug/m3]'], df_final['UBC_PM_04_pm10_cor'], s=size, color = colors[3])
ax.scatter(df_final['PM1 [ug/m3]'], df_final['UBC_PM_05_pm10_cor'], s=size, color = colors[4])
ax.set_ylabel(r'$\frac{\mu g}{m^3}$', rotation=0)
ax.set_xlabel(r'$\frac{\mu g}{m^3}$')

ax = fig.add_subplot(2, 2, 2)
bins = 20
alpha = 0.6
ax.hist(df_final['PM1 [ug/m3]'],bins,alpha = alpha, color = colors[0], zorder = 10)
ax.hist(df_final['UBC_PM_01_pm10_cor'],bins, alpha = alpha, color = colors[1])
# ax.hist(df_final['UBC_PM_02_pm10_env'],bins, alpha = alpha,color = colors[2])
ax.hist(df_final['UBC_PM_03_pm10_cor'],bins, alpha = alpha, color = colors[2])
ax.hist(df_final['UBC_PM_04_pm10_cor'],bins, alpha = alpha,color = colors[3])
ax.hist(df_final['UBC_PM_05_pm10_cor'],bins, alpha = alpha, color = colors[4])
ax.set_ylabel('Count')
ax.set_xlabel(r'$\frac{\mu g}{m^3}$')